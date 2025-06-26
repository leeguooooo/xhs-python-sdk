"""HTTP client implementation for XHS SDK."""

import asyncio
import json
import time
from typing import Any, Dict, Optional, Union

import structlog
from curl_cffi.requests import AsyncSession, Response, Session

from xhs_sdk.constants import (
    API_BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
)
from xhs_sdk.exceptions import (
    XhsAPIError,
    XhsAuthError,
    XhsNetworkError,
    XhsRateLimitError,
)

logger = structlog.get_logger()


class BaseHttpClient:
    """Base HTTP client with common functionality."""
    
    def __init__(
        self,
        cookie: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        debug: bool = False,
        proxy: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize HTTP client.
        
        Args:
            cookie: Authentication cookie
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            debug: Enable debug logging
            proxy: Proxy configuration
        """
        self.cookie = cookie
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.debug = debug
        self.proxy = proxy
        self._base_url = API_BASE_URL
        
        # Configure logging
        if debug:
            structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(
                    logging.DEBUG
                ),
            )
    
    def _parse_cookie(self, cookie: str) -> Dict[str, str]:
        """Parse cookie string into dictionary.
        
        Args:
            cookie: Cookie string
            
        Returns:
            Cookie dictionary
        """
        cookie_dict = {}
        if cookie:
            for pair in cookie.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    cookie_dict[key.strip()] = value.strip()
        return cookie_dict
    
    def _handle_response(self, response: Response) -> Dict[str, Any]:
        """Handle API response and errors.
        
        Args:
            response: HTTP response
            
        Returns:
            Parsed response data
            
        Raises:
            XhsAuthError: Authentication failed
            XhsRateLimitError: Rate limit exceeded
            XhsAPIError: API error
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise XhsAPIError(
                f"Invalid JSON response: {response.text[:200]}"
            )
        
        # Check for API errors
        success = data.get("success", True)
        code = data.get("code", 0)
        
        if not success or code != 0:
            message = data.get("msg", data.get("message", "Unknown error"))
            
            # Handle specific error codes
            if code in [10001, 10002]:  # Auth errors
                raise XhsAuthError(f"Authentication failed: {message}")
            elif code == 10003:  # Rate limit
                raise XhsRateLimitError(
                    f"Rate limit exceeded: {message}",
                    retry_after=60
                )
            else:
                raise XhsAPIError(
                    message=f"API error: {message}",
                    code=code,
                    response=data
                )
        
        return data.get("data", data)
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if request should be retried.
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number
            
        Returns:
            Whether to retry
        """
        if attempt >= self.max_retries:
            return False
            
        # Retry on network errors
        if isinstance(error, XhsNetworkError):
            return True
            
        # Retry on specific API errors
        if isinstance(error, XhsAPIError) and error.code in [500, 502, 503]:
            return True
            
        # Don't retry on auth errors or client errors
        return False


class HttpClient(BaseHttpClient):
    """Synchronous HTTP client for XHS API."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize synchronous HTTP client."""
        super().__init__(*args, **kwargs)
        self._session = None
    
    def _get_session(self) -> Session:
        """Get or create HTTP session.
        
        Returns:
            curl_cffi Session instance
        """
        if self._session is None:
            self._session = Session(
                verify=True,
                impersonate="chrome124",
                timeout=self.timeout,
                proxies=self.proxy,
            )
        return self._session
    
    def request(
        self,
        method: str,
        uri: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retries.
        
        Args:
            method: HTTP method
            uri: API endpoint URI
            headers: Additional headers
            params: Query parameters
            json_data: JSON request body
            
        Returns:
            Response data
            
        Raises:
            XhsNetworkError: Network error
            XhsAPIError: API error
        """
        session = self._get_session()
        url = f"{self._base_url}{uri}"
        
        # Prepare headers
        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare cookies
        cookies = self._parse_cookie(self.cookie)
        
        # Log request if debug
        if self.debug:
            logger.debug(
                "Making request",
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json_data=json_data,
            )
        
        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=json_data,
                    cookies=cookies,
                )
                
                # Check HTTP status
                if response.status_code >= 500:
                    raise XhsAPIError(
                        f"Server error: {response.status_code}",
                        code=response.status_code
                    )
                
                return self._handle_response(response)
                
            except Exception as e:
                last_error = e
                
                # Convert to appropriate exception type
                if not isinstance(e, (XhsAuthError, XhsAPIError, 
                                     XhsRateLimitError)):
                    e = XhsNetworkError(f"Request failed: {str(e)}")
                
                if self._should_retry(e, attempt):
                    if self.debug:
                        logger.debug(
                            f"Retrying request (attempt {attempt + 1})",
                            error=str(e)
                        )
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                raise e
        
        # If we get here, all retries failed
        raise last_error or XhsNetworkError("Request failed after retries")
    
    def close(self) -> None:
        """Close HTTP session."""
        if self._session:
            self._session.close()
            self._session = None


class AsyncHttpClient(BaseHttpClient):
    """Asynchronous HTTP client for XHS API."""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize asynchronous HTTP client."""
        super().__init__(*args, **kwargs)
        self._session = None
    
    async def _get_session(self) -> AsyncSession:
        """Get or create async HTTP session.
        
        Returns:
            curl_cffi AsyncSession instance
        """
        if self._session is None:
            self._session = AsyncSession(
                verify=True,
                impersonate="chrome124",
                timeout=self.timeout,
                proxies=self.proxy,
            )
        return self._session
    
    async def request(
        self,
        method: str,
        uri: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make async HTTP request with retries.
        
        Args:
            method: HTTP method
            uri: API endpoint URI
            headers: Additional headers
            params: Query parameters
            json_data: JSON request body
            
        Returns:
            Response data
            
        Raises:
            XhsNetworkError: Network error
            XhsAPIError: API error
        """
        session = await self._get_session()
        url = f"{self._base_url}{uri}"
        
        # Prepare headers
        request_headers = DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare cookies
        cookies = self._parse_cookie(self.cookie)
        
        # Log request if debug
        if self.debug:
            logger.debug(
                "Making async request",
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json_data=json_data,
            )
        
        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=json_data,
                    cookies=cookies,
                )
                
                # Check HTTP status
                if response.status_code >= 500:
                    raise XhsAPIError(
                        f"Server error: {response.status_code}",
                        code=response.status_code
                    )
                
                # Parse response
                content = await response.acontent()
                response.text = content.decode("utf-8")
                response.json = lambda: json.loads(response.text)
                
                return self._handle_response(response)
                
            except Exception as e:
                last_error = e
                
                # Convert to appropriate exception type
                if not isinstance(e, (XhsAuthError, XhsAPIError, 
                                     XhsRateLimitError)):
                    e = XhsNetworkError(f"Request failed: {str(e)}")
                
                if self._should_retry(e, attempt):
                    if self.debug:
                        logger.debug(
                            f"Retrying async request (attempt {attempt + 1})",
                            error=str(e)
                        )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                raise e
        
        # If we get here, all retries failed
        raise last_error or XhsNetworkError("Request failed after retries")
    
    async def close(self) -> None:
        """Close async HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self) -> "AsyncHttpClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
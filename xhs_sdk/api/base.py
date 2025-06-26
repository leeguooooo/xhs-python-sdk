"""Base API class with common functionality."""

from typing import Any, Dict, Optional, Union

from xhs_sdk.core import AsyncHttpClient, HttpClient, SignatureGenerator


class BaseAPI:
    """Base class for API handlers with common functionality."""
    
    def __init__(
        self,
        http_client: Union[HttpClient, AsyncHttpClient],
        signature_generator: SignatureGenerator,
        cookie: str,
    ) -> None:
        """Initialize BaseAPI.
        
        Args:
            http_client: HTTP client instance
            signature_generator: Signature generator instance
            cookie: Authentication cookie
        """
        self._http_client = http_client
        self._signature_generator = signature_generator
        self._cookie = cookie
        self._is_async = isinstance(http_client, AsyncHttpClient)
    
    def _make_request_sync(
        self,
        method: str,
        uri: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_signature: bool = True,
        include_common: bool = False,
    ) -> Dict[str, Any]:
        """Make synchronous HTTP request with optional signature.
        
        Args:
            method: HTTP method
            uri: API endpoint URI
            data: Request body data
            params: Query parameters
            use_signature: Whether to generate signature headers
            include_common: Whether to include x-s-common header
            
        Returns:
            API response data
        """
        headers = {}
        
        if use_signature and data:
            headers = self._signature_generator.generate_headers(
                uri=uri,
                data=data,
                cookie=self._cookie,
                include_common=include_common,
            )
        
        return self._http_client.request(
            method=method,
            uri=uri,
            headers=headers,
            json_data=data,
            params=params,
        )
    
    async def _make_request_async(
        self,
        method: str,
        uri: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_signature: bool = True,
        include_common: bool = False,
    ) -> Dict[str, Any]:
        """Make asynchronous HTTP request with optional signature.
        
        Args:
            method: HTTP method
            uri: API endpoint URI
            data: Request body data
            params: Query parameters
            use_signature: Whether to generate signature headers
            include_common: Whether to include x-s-common header
            
        Returns:
            API response data
        """
        headers = {}
        
        if use_signature and data:
            headers = self._signature_generator.generate_headers(
                uri=uri,
                data=data,
                cookie=self._cookie,
                include_common=include_common,
            )
        
        return await self._http_client.request(
            method=method,
            uri=uri,
            headers=headers,
            json_data=data,
            params=params,
        )
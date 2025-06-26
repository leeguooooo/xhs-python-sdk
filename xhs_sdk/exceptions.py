"""Exception classes for XHS SDK."""

from typing import Any, Optional


class XhsError(Exception):
    """Base exception for all XHS SDK errors."""
    
    def __init__(self, message: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(message, *args)
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)


class XhsAuthError(XhsError):
    """Raised when authentication fails.
    
    This typically happens when:
    - Cookie is invalid or expired
    - Required authentication headers are missing
    - User lacks permission for the requested resource
    """
    pass


class XhsAPIError(XhsError):
    """Raised when the API returns an error response.
    
    Attributes:
        code: Error code from the API
        message: Error message from the API
        response: Raw response data
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        response: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.response = response


class XhsNetworkError(XhsError):
    """Raised when a network error occurs.
    
    This includes:
    - Connection timeouts
    - DNS resolution failures
    - Connection refused errors
    """
    pass


class XhsRateLimitError(XhsError):
    """Raised when rate limit is exceeded.
    
    Attributes:
        retry_after: Seconds to wait before retrying (if provided)
    """
    
    def __init__(
        self, message: str, retry_after: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class XhsValidationError(XhsError):
    """Raised when input validation fails.
    
    This includes:
    - Invalid parameters
    - Missing required fields
    - Type mismatches
    """
    pass


class XhsSignatureError(XhsError):
    """Raised when signature generation fails.
    
    This might happen if:
    - JavaScript execution fails
    - Required JS files are missing
    - Node.js is not installed
    """
    pass
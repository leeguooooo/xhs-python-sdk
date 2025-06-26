"""User API handlers."""

from typing import Union

from xhs_sdk.constants import Endpoints
from xhs_sdk.core import AsyncHttpClient, HttpClient, SignatureGenerator
from xhs_sdk.models import User


class UserAPI:
    """User-related API operations."""
    
    def __init__(
        self,
        http_client: Union[HttpClient, AsyncHttpClient],
        signature_generator: SignatureGenerator,
    ) -> None:
        """Initialize UserAPI.
        
        Args:
            http_client: HTTP client instance
            signature_generator: Signature generator instance
        """
        self._http_client = http_client
        self._signature_generator = signature_generator
        self._is_async = isinstance(http_client, AsyncHttpClient)
    
    def get_user_profile(self, user_id: str) -> Union[User, "asyncio.Future[User]"]:
        """Get user profile by ID.
        
        Args:
            user_id: Target user ID
            
        Returns:
            User profile (or Future for async)
        """
        if self._is_async:
            return self._get_user_profile_async(user_id)
        else:
            return self._get_user_profile_sync(user_id)
    
    def _get_user_profile_sync(self, user_id: str) -> User:
        """Synchronous implementation."""
        params = {"target_user_id": user_id}
        
        response = self._http_client.request(
            method="GET",
            uri=Endpoints.USER_PROFILE,
            params=params,
        )
        
        return User.from_api_response(response)
    
    async def _get_user_profile_async(self, user_id: str) -> User:
        """Asynchronous implementation."""
        params = {"target_user_id": user_id}
        
        response = await self._http_client.request(
            method="GET",
            uri=Endpoints.USER_PROFILE,
            params=params,
        )
        
        return User.from_api_response(response)
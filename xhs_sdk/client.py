"""Main client implementation for XHS SDK."""

import json
import random
import time
from typing import Any, Dict, List, Optional, Union

from xhs_sdk.api import CommentAPI, NoteAPI, UserAPI
from xhs_sdk.constants import Endpoints
from xhs_sdk.core import AsyncHttpClient, HttpClient, SignatureGenerator
from xhs_sdk.exceptions import XhsValidationError
from xhs_sdk.models import (
    Comment,
    CommentPage,
    Note,
    NoteDetail,
    SearchResult,
    User,
)


class BaseXhsClient:
    """Base client with common functionality."""
    
    def __init__(
        self,
        cookie: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        debug: bool = False,
        proxy: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize XHS client.
        
        Args:
            cookie: Authentication cookie from XHS web
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
            debug: Enable debug logging
            proxy: HTTP/HTTPS proxy configuration
            
        Raises:
            XhsValidationError: If cookie is empty
        """
        if not cookie:
            raise XhsValidationError("Cookie is required")
            
        self.cookie = cookie
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.debug = debug
        self.proxy = proxy
        
        # Initialize components
        self._signature_generator = SignatureGenerator()
        self._init_http_client()
        self._init_apis()
    
    def _init_http_client(self) -> None:
        """Initialize HTTP client (implemented by subclasses)."""
        raise NotImplementedError
    
    def _init_apis(self) -> None:
        """Initialize API handlers."""
        self.user_api = UserAPI(self._http_client, self._signature_generator, self.cookie)
        self.note_api = NoteAPI(self._http_client, self._signature_generator, self.cookie)
        self.comment_api = CommentAPI(
            self._http_client, self._signature_generator, self.cookie
        )
    
    def _generate_search_id(self) -> str:
        """Generate unique search ID.
        
        Returns:
            Base36 encoded search ID
        """
        timestamp = int(time.time() * 1000) << 64
        random_num = int(random.uniform(0, 2147483646))
        number = timestamp + random_num
        
        # Base36 encode
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        base36 = ""
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36
        
        return base36 or "0"


class XhsClient(BaseXhsClient):
    """Synchronous XHS client."""
    
    def _init_http_client(self) -> None:
        """Initialize synchronous HTTP client."""
        self._http_client = HttpClient(
            cookie=self.cookie,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            debug=self.debug,
            proxy=self.proxy,
        )
    
    def get_current_user(self) -> User:
        """Get current authenticated user information.
        
        Returns:
            Current user information
            
        Raises:
            XhsAuthError: If authentication fails
            XhsAPIError: If API request fails
        """
        response = self._http_client.request(
            method="GET",
            uri=Endpoints.USER_ME,
        )
        return User.from_api_response(response)
    
    def get_user_profile(self, user_id: str) -> User:
        """Get user profile by ID.
        
        Args:
            user_id: Target user ID
            
        Returns:
            User profile information
            
        Raises:
            XhsAPIError: If API request fails
        """
        return self.user_api.get_user_profile(user_id)
    
    def search_notes(
        self,
        keyword: str,
        limit: int = 20,
        sort: str = "general",
        note_type: str = "all",
    ) -> List[Note]:
        """Search notes by keyword.
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results (1-100)
            sort: Sort order (general/hot/time)
            note_type: Note type filter (all/normal/video)
            
        Returns:
            List of matching notes
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not keyword:
            raise XhsValidationError("Keyword is required")
        
        if limit < 1 or limit > 100:
            raise XhsValidationError("Limit must be between 1 and 100")
        
        search_result = self.note_api.search_notes(
            keyword=keyword,
            search_id=self._generate_search_id(),
            limit=limit,
            sort=sort,
            note_type=note_type,
        )
        
        return search_result.notes
    
    def get_home_feed(self) -> List[Note]:
        """Get personalized home feed recommendations.
        
        Returns:
            List of recommended notes
            
        Raises:
            XhsAPIError: If API request fails
        """
        return self.note_api.get_home_feed()
    
    def get_note(self, note_id: str, xsec_token: str) -> NoteDetail:
        """Get detailed note information.
        
        Args:
            note_id: Note ID
            xsec_token: Security token from note URL
            
        Returns:
            Detailed note information
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not xsec_token:
            raise XhsValidationError(
                "xsec_token is required. "
                "Get it from the note URL: "
                "https://www.xiaohongshu.com/explore/{note_id}?xsec_token=xxx"
            )
        
        return self.note_api.get_note_detail(
            note_id=note_id,
            xsec_token=xsec_token,
        )
    
    def get_note_comments(
        self,
        note_id: str,
        xsec_token: str,
        cursor: str = "",
    ) -> CommentPage:
        """Get note comments with pagination.
        
        Args:
            note_id: Note ID
            xsec_token: Security token from note URL
            cursor: Pagination cursor (empty for first page)
            
        Returns:
            Comment page with comments and pagination info
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not xsec_token:
            raise XhsValidationError("xsec_token is required")
        
        return self.comment_api.get_comments(
            note_id=note_id,
            xsec_token=xsec_token,
            cursor=cursor,
        )
    
    def post_comment(
        self, 
        note_id: str, 
        content: str,
        target_comment_id: str = "",
        at_users: list = None,
    ) -> Comment:
        """Post a comment to a note.
        
        Args:
            note_id: Target note ID
            content: Comment content
            target_comment_id: ID of comment to reply to (optional)
            at_users: List of user IDs to mention (optional)
            
        Returns:
            Posted comment information
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not content:
            raise XhsValidationError("Comment content is required")
        
        if len(content) > 500:
            raise XhsValidationError("Comment content too long (max 500)")
        
        return self.comment_api.post_comment(
            note_id=note_id,
            content=content,
            target_comment_id=target_comment_id,
            at_users=at_users,
        )
    
    def close(self) -> None:
        """Close client and release resources."""
        self._http_client.close()


class AsyncXhsClient(BaseXhsClient):
    """Asynchronous XHS client."""
    
    def _init_http_client(self) -> None:
        """Initialize asynchronous HTTP client."""
        self._http_client = AsyncHttpClient(
            cookie=self.cookie,
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            debug=self.debug,
            proxy=self.proxy,
        )
    
    async def get_current_user(self) -> User:
        """Get current authenticated user information.
        
        Returns:
            Current user information
            
        Raises:
            XhsAuthError: If authentication fails
            XhsAPIError: If API request fails
        """
        response = await self._http_client.request(
            method="GET",
            uri=Endpoints.USER_ME,
        )
        return User.from_api_response(response)
    
    async def get_user_profile(self, user_id: str) -> User:
        """Get user profile by ID.
        
        Args:
            user_id: Target user ID
            
        Returns:
            User profile information
            
        Raises:
            XhsAPIError: If API request fails
        """
        return await self.user_api.get_user_profile(user_id)
    
    async def search_notes(
        self,
        keyword: str,
        limit: int = 20,
        sort: str = "general",
        note_type: str = "all",
    ) -> List[Note]:
        """Search notes by keyword.
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results (1-100)
            sort: Sort order (general/hot/time)
            note_type: Note type filter (all/normal/video)
            
        Returns:
            List of matching notes
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not keyword:
            raise XhsValidationError("Keyword is required")
        
        if limit < 1 or limit > 100:
            raise XhsValidationError("Limit must be between 1 and 100")
        
        search_result = await self.note_api.search_notes(
            keyword=keyword,
            search_id=self._generate_search_id(),
            limit=limit,
            sort=sort,
            note_type=note_type,
        )
        
        return search_result.notes
    
    async def get_home_feed(self) -> List[Note]:
        """Get personalized home feed recommendations.
        
        Returns:
            List of recommended notes
            
        Raises:
            XhsAPIError: If API request fails
        """
        return await self.note_api.get_home_feed()
    
    async def get_note(self, note_id: str, xsec_token: str) -> NoteDetail:
        """Get detailed note information.
        
        Args:
            note_id: Note ID
            xsec_token: Security token from note URL
            
        Returns:
            Detailed note information
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not xsec_token:
            raise XhsValidationError(
                "xsec_token is required. "
                "Get it from the note URL: "
                "https://www.xiaohongshu.com/explore/{note_id}?xsec_token=xxx"
            )
        
        return await self.note_api.get_note_detail(
            note_id=note_id,
            xsec_token=xsec_token,
        )
    
    async def get_note_comments(
        self,
        note_id: str,
        xsec_token: str,
        cursor: str = "",
    ) -> CommentPage:
        """Get note comments with pagination.
        
        Args:
            note_id: Note ID
            xsec_token: Security token from note URL
            cursor: Pagination cursor (empty for first page)
            
        Returns:
            Comment page with comments and pagination info
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not xsec_token:
            raise XhsValidationError("xsec_token is required")
        
        return await self.comment_api.get_comments(
            note_id=note_id,
            xsec_token=xsec_token,
            cursor=cursor,
        )
    
    async def post_comment(
        self, 
        note_id: str, 
        content: str,
        target_comment_id: str = "",
        at_users: list = None,
    ) -> Comment:
        """Post a comment to a note.
        
        Args:
            note_id: Target note ID
            content: Comment content
            target_comment_id: ID of comment to reply to (optional)
            at_users: List of user IDs to mention (optional)
            
        Returns:
            Posted comment information
            
        Raises:
            XhsValidationError: If parameters are invalid
            XhsAPIError: If API request fails
        """
        if not note_id:
            raise XhsValidationError("Note ID is required")
        
        if not content:
            raise XhsValidationError("Comment content is required")
        
        if len(content) > 500:
            raise XhsValidationError("Comment content too long (max 500)")
        
        return await self.comment_api.post_comment(
            note_id=note_id,
            content=content,
            target_comment_id=target_comment_id,
            at_users=at_users,
        )
    
    async def close(self) -> None:
        """Close client and release resources."""
        await self._http_client.close()
    
    async def __aenter__(self) -> "AsyncXhsClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
"""Comment API handlers."""

from typing import Union

from xhs_sdk.constants import Endpoints, IMAGE_FORMATS
from xhs_sdk.core import AsyncHttpClient, HttpClient, SignatureGenerator
from xhs_sdk.models import Comment, CommentPage


class CommentAPI:
    """Comment-related API operations."""
    
    def __init__(
        self,
        http_client: Union[HttpClient, AsyncHttpClient],
        signature_generator: SignatureGenerator,
    ) -> None:
        """Initialize CommentAPI.
        
        Args:
            http_client: HTTP client instance
            signature_generator: Signature generator instance
        """
        self._http_client = http_client
        self._signature_generator = signature_generator
        self._is_async = isinstance(http_client, AsyncHttpClient)
    
    def get_comments(
        self,
        note_id: str,
        xsec_token: str,
        cursor: str = "",
    ) -> Union[CommentPage, "asyncio.Future[CommentPage]"]:
        """Get note comments with pagination.
        
        Args:
            note_id: Note ID
            xsec_token: Security token
            cursor: Pagination cursor
            
        Returns:
            Comment page (or Future for async)
        """
        if self._is_async:
            return self._get_comments_async(note_id, xsec_token, cursor)
        else:
            return self._get_comments_sync(note_id, xsec_token, cursor)
    
    def _get_comments_sync(
        self,
        note_id: str,
        xsec_token: str,
        cursor: str,
    ) -> CommentPage:
        """Synchronous comment fetching."""
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": ",".join(IMAGE_FORMATS),
            "xsec_token": xsec_token,
        }
        
        response = self._http_client.request(
            method="GET",
            uri=Endpoints.COMMENT_PAGE,
            params=params,
        )
        
        return CommentPage.from_api_response(response)
    
    async def _get_comments_async(
        self,
        note_id: str,
        xsec_token: str,
        cursor: str,
    ) -> CommentPage:
        """Asynchronous comment fetching."""
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": ",".join(IMAGE_FORMATS),
            "xsec_token": xsec_token,
        }
        
        response = await self._http_client.request(
            method="GET",
            uri=Endpoints.COMMENT_PAGE,
            params=params,
        )
        
        return CommentPage.from_api_response(response)
    
    def post_comment(
        self,
        note_id: str,
        content: str,
        cookie: str,
    ) -> Union[Comment, "asyncio.Future[Comment]"]:
        """Post a comment to a note.
        
        Args:
            note_id: Target note ID
            content: Comment content
            cookie: Authentication cookie
            
        Returns:
            Posted comment (or Future for async)
        """
        if self._is_async:
            return self._post_comment_async(note_id, content, cookie)
        else:
            return self._post_comment_sync(note_id, content, cookie)
    
    def _post_comment_sync(
        self,
        note_id: str,
        content: str,
        cookie: str,
    ) -> Comment:
        """Synchronous comment posting."""
        data = {
            "note_id": note_id,
            "content": content,
            "at_users": [],
        }
        
        # Generate signature headers
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.COMMENT_POST,
            data=data,
            cookie=cookie,
        )
        
        response = self._http_client.request(
            method="POST",
            uri=Endpoints.COMMENT_POST,
            headers=headers,
            json_data=data,
        )
        
        # The response contains the new comment
        return Comment.from_api_response(response.get("comment", response))
    
    async def _post_comment_async(
        self,
        note_id: str,
        content: str,
        cookie: str,
    ) -> Comment:
        """Asynchronous comment posting."""
        data = {
            "note_id": note_id,
            "content": content,
            "at_users": [],
        }
        
        # Generate signature headers
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.COMMENT_POST,
            data=data,
            cookie=cookie,
        )
        
        response = await self._http_client.request(
            method="POST",
            uri=Endpoints.COMMENT_POST,
            headers=headers,
            json_data=data,
        )
        
        # The response contains the new comment
        return Comment.from_api_response(response.get("comment", response))
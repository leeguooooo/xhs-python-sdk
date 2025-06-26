"""Comment API handlers."""

import asyncio
from typing import Union

from xhs_sdk.api.base import BaseAPI
from xhs_sdk.constants import Endpoints, IMAGE_FORMATS
from xhs_sdk.models import Comment, CommentPage


class CommentAPI(BaseAPI):
    """Comment-related API operations."""
    
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
        }
        
        # Only add xsec_token if provided
        if xsec_token:
            params["xsec_token"] = xsec_token
        
        response = self._make_request_sync(
            method="GET",
            uri=Endpoints.COMMENT_PAGE,
            params=params,
            use_signature=False,  # GET requests typically don't need signature
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
        }
        
        # Only add xsec_token if provided
        if xsec_token:
            params["xsec_token"] = xsec_token
        
        response = await self._make_request_async(
            method="GET",
            uri=Endpoints.COMMENT_PAGE,
            params=params,
            use_signature=False,  # GET requests typically don't need signature
        )
        
        return CommentPage.from_api_response(response)
    
    def post_comment(
        self,
        note_id: str,
        content: str,
        target_comment_id: str = "",
        at_users: list = None,
    ) -> Union[Comment, "asyncio.Future[Comment]"]:
        """Post a comment to a note.
        
        Args:
            note_id: Target note ID
            content: Comment content
            target_comment_id: ID of comment to reply to (optional)
            at_users: List of user IDs to mention (optional)
            
        Returns:
            Posted comment (or Future for async)
        """
        if at_users is None:
            at_users = []
            
        if self._is_async:
            return self._post_comment_async(note_id, content, target_comment_id, at_users)
        else:
            return self._post_comment_sync(note_id, content, target_comment_id, at_users)
    
    def _post_comment_sync(
        self,
        note_id: str,
        content: str,
        target_comment_id: str,
        at_users: list,
    ) -> Comment:
        """Synchronous comment posting."""
        data = {
            "note_id": note_id,
            "content": content,
            "at_users": at_users,
        }
        
        # Add target_comment_id if it's a reply
        if target_comment_id:
            data["target_comment_id"] = target_comment_id
        
        response = self._make_request_sync(
            method="POST",
            uri=Endpoints.COMMENT_POST,
            data=data,
            use_signature=True,
            include_common=True,  # Comment post needs x-s-common
        )
        
        # The response contains the new comment
        return Comment.from_api_response(response.get("comment", response))
    
    async def _post_comment_async(
        self,
        note_id: str,
        content: str,
        target_comment_id: str,
        at_users: list,
    ) -> Comment:
        """Asynchronous comment posting."""
        data = {
            "note_id": note_id,
            "content": content,
            "at_users": at_users,
        }
        
        # Add target_comment_id if it's a reply
        if target_comment_id:
            data["target_comment_id"] = target_comment_id
        
        response = await self._make_request_async(
            method="POST",
            uri=Endpoints.COMMENT_POST,
            data=data,
            use_signature=True,
            include_common=True,  # Comment post needs x-s-common
        )
        
        # The response contains the new comment
        return Comment.from_api_response(response.get("comment", response))
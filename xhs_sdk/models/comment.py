"""Comment model definitions."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from xhs_sdk.models.user import User


class Comment(BaseModel):
    """Comment information model.
    
    Attributes:
        comment_id: Unique comment identifier
        content: Comment text content
        user: Comment author information
        created_at: Creation timestamp
        likes: Number of likes on this comment
        sub_comments: List of sub-comments (replies)
        is_author: Whether commenter is the note author
        is_liked: Whether current user liked this comment
    """
    
    comment_id: str = Field(..., description="Comment ID")
    content: str = Field(..., description="Comment content")
    user: User = Field(..., description="Comment author")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    likes: int = Field(0, description="Likes count")
    sub_comments: List["Comment"] = Field(
        default_factory=list, description="Sub-comments"
    )
    is_author: bool = Field(False, description="Is note author")
    is_liked: bool = Field(False, description="Liked by current user")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "Comment":
        """Create Comment instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            Comment instance
        """
        # Parse user information
        user_data = data.get("user_info", data.get("user", {}))
        user = User.from_api_response(user_data)
        
        # Parse timestamp
        created_at = None
        if "create_time" in data:
            try:
                created_at = datetime.fromtimestamp(data["create_time"] / 1000)
            except (ValueError, TypeError):
                pass
        
        # Parse sub-comments recursively
        sub_comments = []
        for sub_data in data.get("sub_comments", []):
            sub_comments.append(cls.from_api_response(sub_data))
        
        return cls(
            comment_id=data.get("id", data.get("comment_id", "")),
            content=data.get("content", ""),
            user=user,
            created_at=created_at,
            likes=data.get("like_count", data.get("likes", 0)),
            sub_comments=sub_comments,
            is_author=data.get("is_author", False),
            is_liked=data.get("liked", False),
        )


class CommentPage(BaseModel):
    """Paginated comment list model.
    
    Attributes:
        comments: List of comments on current page
        cursor: Cursor for next page
        has_more: Whether more comments are available
        total: Total number of comments
    """
    
    comments: List[Comment] = Field(
        default_factory=list, description="Comments list"
    )
    cursor: str = Field("", description="Pagination cursor")
    has_more: bool = Field(False, description="Has more comments")
    total: int = Field(0, description="Total comments count")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "CommentPage":
        """Create CommentPage instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            CommentPage instance
        """
        comments_data = data.get("comments", [])
        comments = [Comment.from_api_response(c) for c in comments_data]
        
        return cls(
            comments=comments,
            cursor=data.get("cursor", ""),
            has_more=data.get("has_more", False),
            total=data.get("total", len(comments)),
        )


# Update forward references
Comment.model_rebuild()
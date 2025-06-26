"""User model definitions."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User information model.
    
    Attributes:
        user_id: Unique user identifier
        nickname: User's display name
        avatar: URL to user's avatar image
        description: User's bio/description
        gender: User's gender (0: unknown, 1: male, 2: female)
        followers: Number of followers
        following: Number of users being followed
        notes_count: Total number of notes published
        liked_count: Total number of likes received
        collected_count: Total number of collections
        is_verified: Whether the user is verified
        level: User level information
    """
    
    user_id: str = Field(..., description="User ID")
    nickname: str = Field(..., description="User nickname")
    avatar: Optional[str] = Field(None, description="Avatar URL")
    description: Optional[str] = Field("", description="User bio")
    gender: int = Field(0, description="Gender: 0=unknown, 1=male, 2=female")
    followers: int = Field(0, description="Followers count")
    following: int = Field(0, description="Following count")
    notes_count: int = Field(0, description="Notes count")
    liked_count: int = Field(0, description="Total likes received")
    collected_count: int = Field(0, description="Total collections")
    is_verified: bool = Field(False, description="Verification status")
    level: Optional[dict] = Field(None, description="User level info")
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @classmethod
    def from_api_response(cls, data: dict) -> "User":
        """Create User instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            User instance
        """
        return cls(
            user_id=data.get("user_id", data.get("id", "")),
            nickname=data.get("nickname", ""),
            avatar=data.get("avatar", data.get("images", "")),
            description=data.get("desc", data.get("description", "")),
            gender=data.get("gender", 0),
            followers=data.get("fans", data.get("followers", 0)),
            following=data.get("follows", data.get("following", 0)),
            notes_count=data.get("notes", data.get("notes_count", 0)),
            liked_count=data.get("liked", data.get("liked_count", 0)),
            collected_count=data.get("collected", 
                                   data.get("collected_count", 0)),
            is_verified=data.get("verified", False),
            level=data.get("level", None),
        )
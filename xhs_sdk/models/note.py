"""Note model definitions."""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from xhs_sdk.models.user import User


class Note(BaseModel):
    """Basic note information model.
    
    Attributes:
        note_id: Unique note identifier
        title: Note title
        description: Note description/preview
        author: Note author information
        images: List of image URLs
        video: Video information if available
        likes: Number of likes
        comments: Number of comments  
        collects: Number of collections
        shares: Number of shares
        tags: List of tags
        created_at: Creation timestamp
        note_type: Type of note (normal/video)
    """
    
    note_id: str = Field(..., description="Note ID")
    title: str = Field(..., description="Note title")
    description: str = Field("", description="Note description")
    author: User = Field(..., description="Author information")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    video: Optional[dict] = Field(None, description="Video info")
    likes: int = Field(0, description="Likes count")
    comments: int = Field(0, description="Comments count")
    collects: int = Field(0, description="Collections count")
    shares: int = Field(0, description="Shares count")
    tags: List[str] = Field(default_factory=list, description="Tags")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    note_type: str = Field("normal", description="Note type")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "Note":
        """Create Note instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            Note instance
        """
        # Parse author information
        author_data = data.get("user", {})
        author = User.from_api_response(author_data)
        
        # Parse images
        images = []
        if "image_list" in data:
            # Search result format
            images = [img.get("url_default", img.get("url", "")) for img in data["image_list"]]
        elif "images_list" in data:
            images = [img.get("url", "") for img in data["images_list"]]
        elif "images" in data:
            images = data["images"] if isinstance(data["images"], list) else []
        elif "cover" in data:
            # Use cover image if no image list
            cover_url = data["cover"].get("url_default", data["cover"].get("url", ""))
            if cover_url:
                images = [cover_url]
        
        # Parse interaction info (likes, comments, etc.)
        interact_info = data.get("interact_info", {})
        likes = interact_info.get("liked_count", data.get("likes_count", 0))
        comments = interact_info.get("comment_count", data.get("comments_count", 0))
        collects = interact_info.get("collected_count", data.get("collected_count", 0))
        shares = interact_info.get("shared_count", data.get("share_count", 0))
        
        # Convert string counts to integers
        def to_int(val):
            if isinstance(val, str):
                return int(val.replace(",", "").replace("k", "000").replace("w", "0000"))
            return int(val or 0)
        
        # Parse timestamp
        created_at = None
        if "time" in data:
            try:
                created_at = datetime.fromtimestamp(data["time"] / 1000)
            except (ValueError, TypeError):
                pass
        
        return cls(
            note_id=data.get("note_id", data.get("id", "")),
            title=data.get("title", data.get("display_title", "")),
            description=data.get("desc", data.get("description", "")),
            author=author,
            images=images,
            video=data.get("video", None),
            likes=to_int(likes),
            comments=to_int(comments),
            collects=to_int(collects),
            shares=to_int(shares),
            tags=[tag.get("name", "") for tag in data.get("tags", [])],
            created_at=created_at,
            note_type=data.get("type", "normal"),
        )


class NoteDetail(Note):
    """Detailed note information model.
    
    Extends Note with additional fields available when fetching
    individual note details.
    
    Additional Attributes:
        content: Full note content
        updated_at: Last update timestamp
        location: Location information
        is_liked: Whether current user liked this note
        is_collected: Whether current user collected this note
    """
    
    content: str = Field("", description="Full note content")
    updated_at: Optional[datetime] = Field(None, description="Update time")
    location: Optional[dict] = Field(None, description="Location info")
    is_liked: bool = Field(False, description="Liked by current user")
    is_collected: bool = Field(False, description="Collected by current user")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "NoteDetail":
        """Create NoteDetail instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            NoteDetail instance
        """
        # Get base note data
        note_data = data.get("items", [{}])[0] if "items" in data else data
        base_note = Note.from_api_response(note_data).dict()
        
        # Add detailed fields
        base_note.update({
            "content": note_data.get("desc", ""),
            "location": note_data.get("location", None),
            "is_liked": note_data.get("liked", False),
            "is_collected": note_data.get("collected", False),
        })
        
        # Parse updated_at
        if "last_update_time" in note_data:
            try:
                base_note["updated_at"] = datetime.fromtimestamp(
                    note_data["last_update_time"] / 1000
                )
            except (ValueError, TypeError):
                pass
        
        return cls(**base_note)


class SearchResult(BaseModel):
    """Search result model.
    
    Attributes:
        notes: List of notes matching the search
        total: Total number of results
        has_more: Whether more results are available
    """
    
    notes: List[Note] = Field(default_factory=list, description="Notes list")
    total: int = Field(0, description="Total results count")
    has_more: bool = Field(False, description="Has more results")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "SearchResult":
        """Create SearchResult instance from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            SearchResult instance
        """
        items = data.get("items", [])
        notes = []
        
        for item in items:
            # Search results have a different structure with note_card
            if "note_card" in item:
                note_data = item["note_card"]
                # Add missing fields that Note.from_api_response expects
                note_data["note_id"] = item.get("id", "")
                note_data["xsec_token"] = item.get("xsec_token", "")
                # Use display_title as title
                if "display_title" in note_data:
                    note_data["title"] = note_data["display_title"]
                notes.append(Note.from_api_response(note_data))
            else:
                # Regular note structure
                notes.append(Note.from_api_response(item))
        
        return cls(
            notes=notes,
            total=data.get("total", len(notes)),
            has_more=data.get("has_more", False),
        )
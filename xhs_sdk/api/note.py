"""Note API handlers."""

import json
from typing import List, Union

from xhs_sdk.constants import Endpoints, IMAGE_FORMATS, XS_COMMON_HEADER
from xhs_sdk.core import AsyncHttpClient, HttpClient, SignatureGenerator
from xhs_sdk.models import Note, NoteDetail, SearchResult


class NoteAPI:
    """Note-related API operations."""
    
    def __init__(
        self,
        http_client: Union[HttpClient, AsyncHttpClient],
        signature_generator: SignatureGenerator,
    ) -> None:
        """Initialize NoteAPI.
        
        Args:
            http_client: HTTP client instance
            signature_generator: Signature generator instance
        """
        self._http_client = http_client
        self._signature_generator = signature_generator
        self._is_async = isinstance(http_client, AsyncHttpClient)
    
    def search_notes(
        self,
        keyword: str,
        search_id: str,
        limit: int = 20,
        sort: str = "general",
        note_type: str = "all",
    ) -> Union[SearchResult, "asyncio.Future[SearchResult]"]:
        """Search notes by keyword.
        
        Args:
            keyword: Search keyword
            search_id: Unique search ID
            limit: Result limit
            sort: Sort order
            note_type: Note type filter
            
        Returns:
            Search results (or Future for async)
        """
        if self._is_async:
            return self._search_notes_async(
                keyword, search_id, limit, sort, note_type
            )
        else:
            return self._search_notes_sync(
                keyword, search_id, limit, sort, note_type
            )
    
    def _search_notes_sync(
        self,
        keyword: str,
        search_id: str,
        limit: int,
        sort: str,
        note_type: str,
    ) -> SearchResult:
        """Synchronous search implementation."""
        data = {
            "keyword": keyword,
            "page": 1,
            "page_size": limit,
            "search_id": search_id,
            "sort": sort,
            "note_type": 0 if note_type == "all" else (1 if note_type == "normal" else 2),
            "ext_flags": [],
            "geo": "",
            "image_formats": json.dumps(IMAGE_FORMATS, separators=(",", ":")),
        }
        
        response = self._http_client.request(
            method="POST",
            uri=Endpoints.SEARCH_NOTES,
            json_data=data,
        )
        
        return SearchResult.from_api_response(response)
    
    async def _search_notes_async(
        self,
        keyword: str,
        search_id: str,
        limit: int,
        sort: str,
        note_type: str,
    ) -> SearchResult:
        """Asynchronous search implementation."""
        data = {
            "keyword": keyword,
            "page": 1,
            "page_size": limit,
            "search_id": search_id,
            "sort": sort,
            "note_type": 0 if note_type == "all" else (1 if note_type == "normal" else 2),
            "ext_flags": [],
            "geo": "",
            "image_formats": json.dumps(IMAGE_FORMATS, separators=(",", ":")),
        }
        
        response = await self._http_client.request(
            method="POST",
            uri=Endpoints.SEARCH_NOTES,
            json_data=data,
        )
        
        return SearchResult.from_api_response(response)
    
    def get_home_feed(self, cookie: str) -> Union[List[Note], "asyncio.Future[List[Note]]"]:
        """Get home feed recommendations.
        
        Args:
            cookie: Authentication cookie
            
        Returns:
            List of notes (or Future for async)
        """
        if self._is_async:
            return self._get_home_feed_async(cookie)
        else:
            return self._get_home_feed_sync(cookie)
    
    def _get_home_feed_sync(self, cookie: str) -> List[Note]:
        """Synchronous home feed implementation."""
        data = {
            "category": "homefeed_recommend",
            "cursor_score": "",
            "image_formats": json.dumps(IMAGE_FORMATS, separators=(",", ":")),
            "need_filter_image": False,
            "need_num": 8,
            "num": 18,
            "note_index": 33,
            "refresh_type": 1,
            "search_key": "",
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
        }
        
        # Generate signature headers
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.HOME_FEED,
            data=data,
            cookie=cookie,
        )
        
        response = self._http_client.request(
            method="POST",
            uri=Endpoints.HOME_FEED,
            headers=headers,
            json_data=data,
        )
        
        items = response.get("items", [])
        return [Note.from_api_response(item) for item in items]
    
    async def _get_home_feed_async(self, cookie: str) -> List[Note]:
        """Asynchronous home feed implementation."""
        data = {
            "category": "homefeed_recommend",
            "cursor_score": "",
            "image_formats": json.dumps(IMAGE_FORMATS, separators=(",", ":")),
            "need_filter_image": False,
            "need_num": 8,
            "num": 18,
            "note_index": 33,
            "refresh_type": 1,
            "search_key": "",
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
        }
        
        # Generate signature headers
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.HOME_FEED,
            data=data,
            cookie=cookie,
        )
        
        response = await self._http_client.request(
            method="POST",
            uri=Endpoints.HOME_FEED,
            headers=headers,
            json_data=data,
        )
        
        items = response.get("items", [])
        return [Note.from_api_response(item) for item in items]
    
    def get_note_detail(
        self,
        note_id: str,
        xsec_token: str,
        cookie: str,
    ) -> Union[NoteDetail, "asyncio.Future[NoteDetail]"]:
        """Get detailed note information.
        
        Args:
            note_id: Note ID
            xsec_token: Security token
            cookie: Authentication cookie
            
        Returns:
            Note details (or Future for async)
        """
        if self._is_async:
            return self._get_note_detail_async(note_id, xsec_token, cookie)
        else:
            return self._get_note_detail_sync(note_id, xsec_token, cookie)
    
    def _get_note_detail_sync(
        self,
        note_id: str,
        xsec_token: str,
        cookie: str,
    ) -> NoteDetail:
        """Synchronous note detail implementation."""
        data = {
            "source_note_id": note_id,
            "image_formats": IMAGE_FORMATS,
            "extra": {"need_body_topic": "1"},
            "xsec_source": "pc_feed",
            "xsec_token": xsec_token,
        }
        
        # Generate signature headers with x-s-common
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.NOTE_FEED,
            data=data,
            cookie=cookie,
            include_common=True,
        )
        
        response = self._http_client.request(
            method="POST",
            uri=Endpoints.NOTE_FEED,
            headers=headers,
            json_data=data,
        )
        
        return NoteDetail.from_api_response(response)
    
    async def _get_note_detail_async(
        self,
        note_id: str,
        xsec_token: str,
        cookie: str,
    ) -> NoteDetail:
        """Asynchronous note detail implementation."""
        data = {
            "source_note_id": note_id,
            "image_formats": IMAGE_FORMATS,
            "extra": {"need_body_topic": "1"},
            "xsec_source": "pc_feed",
            "xsec_token": xsec_token,
        }
        
        # Generate signature headers with x-s-common
        headers = self._signature_generator.generate_headers(
            uri=Endpoints.NOTE_FEED,
            data=data,
            cookie=cookie,
            include_common=True,
        )
        
        response = await self._http_client.request(
            method="POST",
            uri=Endpoints.NOTE_FEED,
            headers=headers,
            json_data=data,
        )
        
        return NoteDetail.from_api_response(response)
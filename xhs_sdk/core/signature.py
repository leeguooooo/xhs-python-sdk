"""Signature generation for XHS API requests."""

import json
import os
from typing import Any, Dict, Tuple

import execjs

from xhs_sdk.exceptions import XhsSignatureError


class SignatureGenerator:
    """Generate x-s and x-t signatures for API requests.
    
    This class handles the JavaScript-based signature generation
    required for XHS API authentication.
    """
    
    def __init__(self) -> None:
        """Initialize the signature generator."""
        self._js_context = None
        self._js_file_path = os.path.join(
            os.path.dirname(__file__), "signature.js"
        )
        
    def _load_js_context(self) -> execjs.ExternalRuntime.Context:
        """Load JavaScript context for signature generation.
        
        Returns:
            JavaScript execution context
            
        Raises:
            XhsSignatureError: If JS file cannot be loaded
        """
        if self._js_context is None:
            try:
                with open(self._js_file_path, "r", encoding="utf-8") as f:
                    js_code = f.read()
                self._js_context = execjs.compile(js_code)
            except FileNotFoundError:
                raise XhsSignatureError(
                    f"Signature JS file not found: {self._js_file_path}"
                )
            except Exception as e:
                raise XhsSignatureError(
                    f"Failed to load signature JS: {str(e)}"
                )
        return self._js_context
    
    def generate(
        self, 
        uri: str, 
        data: Dict[str, Any], 
        cookie: str
    ) -> Tuple[str, str]:
        """Generate x-s and x-t signatures.
        
        Args:
            uri: API endpoint URI
            data: Request data
            cookie: Authentication cookie
            
        Returns:
            Tuple of (x-s, x-t) signatures
            
        Raises:
            XhsSignatureError: If signature generation fails
        """
        try:
            context = self._load_js_context()
            result = context.call("GetXsXt", uri, data, cookie)
            
            if isinstance(result, str):
                result = json.loads(result)
                
            x_s = result.get("X-s", "")
            x_t = str(result.get("X-t", ""))
            
            if not x_s or not x_t:
                raise XhsSignatureError(
                    "Invalid signature response: missing X-s or X-t"
                )
                
            return x_s, x_t
            
        except execjs.RuntimeUnavailable:
            raise XhsSignatureError(
                "Node.js is required for signature generation. "
                "Please install Node.js 14+ from https://nodejs.org/"
            )
        except Exception as e:
            if isinstance(e, XhsSignatureError):
                raise
            raise XhsSignatureError(
                f"Signature generation failed: {str(e)}"
            )
    
    def generate_headers(
        self,
        uri: str,
        data: Dict[str, Any],
        cookie: str,
        include_common: bool = False
    ) -> Dict[str, str]:
        """Generate signature headers for request.
        
        Args:
            uri: API endpoint URI
            data: Request data
            cookie: Authentication cookie
            include_common: Whether to include x-s-common header
            
        Returns:
            Dictionary with signature headers
        """
        x_s, x_t = self.generate(uri, data, cookie)
        
        headers = {
            "x-s": x_s,
            "x-t": x_t,
        }
        
        if include_common:
            from xhs_sdk.constants import XS_COMMON_HEADER
            headers["x-s-common"] = XS_COMMON_HEADER
            
        return headers
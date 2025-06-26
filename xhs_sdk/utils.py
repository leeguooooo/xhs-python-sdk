"""Utility functions for XHS SDK"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


def load_local_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from local config file.
    
    Args:
        config_path: Optional path to config file. 
                    Defaults to 'config.local.json' in project root.
    
    Returns:
        Dictionary containing config data, or empty dict if not found.
    """
    if config_path is None:
        # Try to find config.local.json in project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        config_path = project_root / "config.local.json"
    else:
        config_path = Path(config_path)
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            return {}
    else:
        return {}


def get_cookie_from_config() -> Optional[str]:
    """Get cookie from local config file.
    
    Returns:
        Cookie string if found, None otherwise.
    """
    config = load_local_config()
    return config.get('cookie')


def get_cookie() -> Optional[str]:
    """Get cookie from various sources in order of priority.
    
    Priority:
    1. XHS_COOKIE environment variable
    2. config.local.json file
    3. None
    
    Returns:
        Cookie string if found, None otherwise.
    """
    # First try environment variable
    cookie = os.getenv('XHS_COOKIE')
    if cookie:
        return cookie
    
    # Then try local config file
    cookie = get_cookie_from_config()
    if cookie:
        return cookie
    
    return None
"""XHS Python SDK - For Learning Purposes Only.

This SDK provides a Python interface to XiaoHongShu's web API.
It is intended for educational and research purposes only.
Commercial use is strictly prohibited.
"""

from xhs_sdk.client import AsyncXhsClient, XhsClient
from xhs_sdk.exceptions import (
    XhsAPIError,
    XhsAuthError,
    XhsError,
    XhsNetworkError,
    XhsRateLimitError,
)

__version__ = "0.1.0"
__author__ = "XHS SDK Contributors"
__license__ = "MIT (Educational Use Only)"

__all__ = [
    "XhsClient",
    "AsyncXhsClient",
    "XhsError",
    "XhsAuthError",
    "XhsAPIError",
    "XhsNetworkError",
    "XhsRateLimitError",
]
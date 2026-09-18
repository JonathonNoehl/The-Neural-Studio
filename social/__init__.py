"""Public social domain for The Neural Studio.

This package is intentionally isolated from the studio-generation logic. It
models the user identity references, public track publishing, feed retrieval,
download counting, and token rewards that are part of the product's social
feature set.
"""

from .models import DownloadResult, TokenTransaction, Track, User
from .repository import InMemorySocialRepository, SocialRepository
from .service import SocialSpaceService

__all__ = [
    "DownloadResult",
    "InMemorySocialRepository",
    "SocialRepository",
    "SocialSpaceService",
    "TokenTransaction",
    "Track",
    "User",
]

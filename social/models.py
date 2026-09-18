from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    id: str
    display_name: str
    bio: str = ""


@dataclass
class Track:
    id: str
    owner_id: str
    title: str
    description: str
    audio_url: str
    artwork_url: Optional[str]
    published_at: datetime
    is_public: bool = True
    download_count: int = 0


@dataclass(frozen=True)
class TokenTransaction:
    id: str
    user_id: str
    amount: int
    transaction_type: str
    reason: str
    track_id: str
    created_at: datetime


@dataclass(frozen=True)
class DownloadResult:
    track_id: str
    counted: bool
    new_download_count: int
    tokens_awarded: int
    token_balance: int

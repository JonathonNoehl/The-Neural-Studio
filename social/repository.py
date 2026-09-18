from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, Set

from .models import Track, User


class SocialRepository(Protocol):
    """Persistence contract used by the social service layer."""

    @abstractmethod
    def get_user(self, user_id: str) -> User: ...

    @abstractmethod
    def save_user(self, user: User) -> None: ...

    @abstractmethod
    def save_track(self, track: Track) -> None: ...

    @abstractmethod
    def get_track(self, track_id: str) -> Track: ...

    @abstractmethod
    def list_public_tracks(self, limit: int, offset: int) -> List[Track]: ...

    @abstractmethod
    def has_downloaded(self, track_id: str, downloader_id: str) -> bool: ...

    @abstractmethod
    def record_download(self, track_id: str, downloader_id: str) -> None: ...

    @abstractmethod
    def add_tokens(self, user_id: str, amount: int, reason: str, track_id: str, transaction_type: str = "social_download_reward") -> int: ...

    @abstractmethod
    def get_token_balance(self, user_id: str) -> int: ...


class InMemorySocialRepository:
    """Reference implementation for local testing and module validation.

    Replace this with an Azure-backed repository before production use.
    """

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.tracks: Dict[str, Track] = {}
        self.downloads: Set[tuple[str, str]] = set()
        self.transactions: List = []
        self.balances: Dict[str, int] = {}

    def get_user(self, user_id: str) -> User:
        try:
            return self.users[user_id]
        except KeyError as exc:
            raise KeyError(f"User {user_id!r} was not found") from exc

    def save_user(self, user: User) -> None:
        self.users[user.id] = user
        self.balances.setdefault(user.id, 0)

    def save_track(self, track: Track) -> None:
        self.tracks[track.id] = track

    def get_track(self, track_id: str) -> Track:
        try:
            return self.tracks[track_id]
        except KeyError as exc:
            raise KeyError(f"Track {track_id!r} was not found") from exc

    def list_public_tracks(self, limit: int, offset: int) -> List[Track]:
        tracks = [track for track in self.tracks.values() if track.is_public]
        tracks.sort(key=lambda track: track.published_at, reverse=True)
        return tracks[offset : offset + limit]

    def has_downloaded(self, track_id: str, downloader_id: str) -> bool:
        return (track_id, downloader_id) in self.downloads

    def record_download(self, track_id: str, downloader_id: str) -> None:
        self.downloads.add((track_id, downloader_id))

    def add_tokens(self, user_id: str, amount: int, reason: str, track_id: str, transaction_type: str = "social_download_reward") -> int:
        if amount <= 0:
            raise ValueError("Token amount must be positive")
        self.get_user(user_id)
        self.balances[user_id] = self.balances.get(user_id, 0) + amount
        self.transactions.append({
            "user_id": user_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "reason": reason,
            "track_id": track_id,
        })
        return self.balances[user_id]

    def get_token_balance(self, user_id: str) -> int:
        self.get_user(user_id)
        return self.balances.get(user_id, 0)

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .models import DownloadResult, Track, User
from .repository import InMemorySocialRepository, SocialRepository


class SocialSpaceService:
    """Application service for the public social layer.

    The Studio domain remains separate.  The social layer only manages public
    track publishing, feed viewing, unique-download tracking, and token rewards.
    """

    def __init__(self, repository: SocialRepository, downloads_per_token: int = 10) -> None:
        if downloads_per_token < 1:
            raise ValueError("downloads_per_token must be at least 1")
        self.repository = repository
        self.downloads_per_token = downloads_per_token

    def create_user(self, display_name: str, bio: str = "") -> User:
        display_name = display_name.strip()
        if not display_name:
            raise ValueError("display_name is required")
        user = User(id=str(uuid4()), display_name=display_name, bio=bio.strip())
        self.repository.save_user(user)
        return user

    def publish_track(
        self,
        owner_id: str,
        title: str,
        audio_url: str,
        description: str = "",
        artwork_url: Optional[str] = None,
        is_public: bool = True,
    ) -> Track:
        self.repository.get_user(owner_id)
        title = title.strip()
        audio_url = audio_url.strip()
        if not title or not audio_url:
            raise ValueError("title and audio_url are required")

        track = Track(
            id=str(uuid4()),
            owner_id=owner_id,
            title=title,
            description=description.strip(),
            audio_url=audio_url,
            artwork_url=artwork_url,
            published_at=datetime.now(timezone.utc),
            is_public=is_public,
        )
        self.repository.save_track(track)
        return track

    def feed(self, limit: int = 20, offset: int = 0) -> list[Track]:
        if limit <= 0 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        if offset < 0:
            raise ValueError("offset cannot be negative")
        return self.repository.list_public_tracks(limit=limit, offset=offset)

    def record_download(self, track_id: str, downloader_id: str) -> DownloadResult:
        downloader_id = downloader_id.strip()
        if not downloader_id:
            raise ValueError("downloader_id is required")

        track = self.repository.get_track(track_id)
        if not track.is_public:
            raise ValueError("This track is not public")

        if self.repository.has_downloaded(track_id, downloader_id):
            return DownloadResult(
                track_id=track.id,
                counted=False,
                new_download_count=track.download_count,
                tokens_awarded=0,
                token_balance=self.repository.get_token_balance(track.owner_id),
            )

        self.repository.record_download(track_id, downloader_id)
        track.download_count += 1

        tokens_awarded = 0
        if track.download_count % self.downloads_per_token == 0:
            tokens_awarded = 1
            self.repository.add_tokens(
                track.owner_id,
                tokens_awarded,
                reason=f"{self.downloads_per_token} verified downloads reached",
                track_id=track.id,
                transaction_type="social_download_reward",
            )

        return DownloadResult(
            track_id=track.id,
            counted=True,
            new_download_count=track.download_count,
            tokens_awarded=tokens_awarded,
            token_balance=self.repository.get_token_balance(track.owner_id),
        )

    def token_balance(self, user_id: str) -> int:
        return self.repository.get_token_balance(user_id)


__all__ = ["SocialSpaceService"]

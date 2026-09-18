import unittest

from social import SocialSpaceService
from social.repository import InMemorySocialRepository


class SocialSpaceServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemorySocialRepository()
        self.service = SocialSpaceService(self.repository, downloads_per_token=2)
        self.creator = self.service.create_user("Creator")
        self.listener = self.service.create_user("Listener")
        self.track = self.service.publish_track(
            self.creator.id,
            "Sunrise Session",
            "https://example.com/audio/sunrise.mp3",
            description="A community release",
        )

    def test_feed_returns_public_tracks(self):
        tracks = self.service.feed()
        self.assertEqual(1, len(tracks))
        self.assertEqual(self.track.id, tracks[0].id)

    def test_duplicate_download_does_not_double_count(self):
        first = self.service.record_download(self.track.id, self.listener.id)
        second = self.service.record_download(self.track.id, self.listener.id)
        self.assertTrue(first.counted)
        self.assertFalse(second.counted)
        self.assertEqual(1, self.track.download_count)

    def test_token_reward_happens_only_after_threshold(self):
        first = self.service.record_download(self.track.id, self.listener.id)
        second = self.service.record_download(self.track.id, "another-listener")

        self.assertEqual(1, first.new_download_count)
        self.assertEqual(0, first.tokens_awarded)
        self.assertEqual(2, second.new_download_count)
        self.assertEqual(1, second.tokens_awarded)
        self.assertEqual(1, self.service.token_balance(self.creator.id))


if __name__ == "__main__":
    unittest.main()

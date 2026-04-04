import sys
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock

import yt2mp3


class TestParseUrls(unittest.TestCase):
    def test_parse_urls_valid(self):
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://www.youtube.com/watch?v=aaa\n")
            f.write("https://youtu.be/bbb\n")
            path = f.name
        result = yt2mp3.parse_urls(path)
        self.assertEqual(result, [
            "https://www.youtube.com/watch?v=aaa",
            "https://youtu.be/bbb",
        ])

    def test_parse_urls_skips_blanks_and_comments(self):
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# 這是註解\n")
            f.write("\n")
            f.write("https://www.youtube.com/watch?v=ccc\n")
            f.write("   \n")
            path = f.name
        result = yt2mp3.parse_urls(path)
        self.assertEqual(result, ["https://www.youtube.com/watch?v=ccc"])


class TestIsValidYoutubeUrl(unittest.TestCase):
    def test_accepts_standard(self):
        self.assertTrue(yt2mp3.is_valid_youtube_url(
            "https://www.youtube.com/watch?v=XXXXXXXXXXX"
        ))

    def test_accepts_short(self):
        self.assertTrue(yt2mp3.is_valid_youtube_url(
            "https://youtu.be/XXXXXXXXXXX"
        ))

    def test_accepts_playlist(self):
        self.assertTrue(yt2mp3.is_valid_youtube_url(
            "https://www.youtube.com/playlist?list=XXXXXXXXXXX"
        ))

    def test_accepts_video_with_list(self):
        self.assertTrue(yt2mp3.is_valid_youtube_url(
            "https://www.youtube.com/watch?v=AAA&list=BBB"
        ))

    def test_rejects_other(self):
        self.assertFalse(yt2mp3.is_valid_youtube_url("https://example.com/video"))
        self.assertFalse(yt2mp3.is_valid_youtube_url("not-a-url"))


class TestDownloadAudio(unittest.TestCase):
    @patch("yt2mp3.subprocess.run")
    def test_calls_yt_dlp(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        yt2mp3.download_audio("https://youtu.be/aaa", Path("/tmp/out"))
        args = mock_run.call_args[0][0]
        self.assertIn("yt-dlp", args[0])
        self.assertIn("https://youtu.be/aaa", args)

    @patch("yt2mp3.subprocess.run")
    def test_creates_output_dir(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_output"
            yt2mp3.download_audio("https://youtu.be/aaa", new_dir)
            self.assertTrue(new_dir.exists())


class TestMain(unittest.TestCase):
    def test_exits_on_missing_file(self):
        with self.assertRaises(SystemExit):
            yt2mp3.main(["non_existent_file.txt"])


if __name__ == "__main__":
    unittest.main()

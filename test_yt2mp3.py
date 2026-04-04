import sys
import tempfile
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


class TestLogging(unittest.TestCase):
    def test_verbose_flag_sets_debug_logging(self):
        import logging
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://www.youtube.com/watch?v=aaa\n")
            path = f.name
        with patch("yt2mp3.download_audio"):
            yt2mp3.main([path, "-v"])
        self.assertEqual(logging.getLogger("yt2mp3").level, logging.DEBUG)

    def test_default_logging_is_warning(self):
        import logging
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://www.youtube.com/watch?v=aaa\n")
            path = f.name
        with patch("yt2mp3.download_audio"):
            yt2mp3.main([path])
        self.assertEqual(logging.getLogger("yt2mp3").level, logging.WARNING)


class TestCollectUrlFiles(unittest.TestCase):
    def test_collect_url_files_from_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "music").mkdir()
            (root / "podcast").mkdir()
            (root / "music" / "urls.txt").write_text("https://youtu.be/aaa\n")
            (root / "podcast" / "urls.txt").write_text("https://youtu.be/bbb\n")

            result = yt2mp3.collect_url_files(root)
            rel_paths = sorted(str(r) for _, r in result)
            self.assertEqual(rel_paths, ["music/urls.txt", "podcast/urls.txt"])

    def test_output_mirrors_input_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "input"
            output_dir = root / "output"
            (input_dir / "music").mkdir(parents=True)
            url_file = input_dir / "music" / "urls.txt"
            url_file.write_text("https://youtu.be/aaa\n")

            files = yt2mp3.collect_url_files(input_dir)
            with patch("yt2mp3.download_audio") as mock_dl:
                for abs_path, rel_path in files:
                    urls = yt2mp3.parse_urls(str(abs_path))
                    dest = output_dir / rel_path.parent
                    for url in urls:
                        yt2mp3.download_audio(url, dest)
                call_args = mock_dl.call_args[0]
                self.assertEqual(call_args[1], output_dir / "music")


class TestMain(unittest.TestCase):
    def test_exits_on_missing_file(self):
        with self.assertRaises(SystemExit):
            yt2mp3.main(["non_existent_file.txt"])


if __name__ == "__main__":
    unittest.main()

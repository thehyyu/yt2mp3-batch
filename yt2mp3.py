import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path

# venv 內的 yt-dlp，若不在 venv 則 fallback 到系統路徑
_YTDLP = str(Path(sys.executable).parent / "yt-dlp")

logger = logging.getLogger("yt2mp3")

YOUTUBE_PATTERN = re.compile(
    r"https?://(www\.)?(youtube\.com/(watch\?.*v=|playlist\?.*list=)|youtu\.be/)\S+"
)


def is_valid_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_PATTERN.match(url))


def parse_urls(file_path: str) -> list:
    logger.debug("解析 URL 檔案：%s", file_path)
    lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    urls = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    logger.debug("找到 %d 個 URL", len(urls))
    return urls


def download_audio(url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        _YTDLP,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        url,
    ]
    logger.debug("執行指令：%s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main(args=None):
    parser = argparse.ArgumentParser(description="批次下載 YouTube 音訊並轉為 MP3")
    parser.add_argument("file", help="包含 YouTube URL 的純文字檔")
    parser.add_argument("-o", "--output", default="output", help="輸出目錄（預設：output）")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示除錯 log")
    parsed = parser.parse_args(args)

    level = logging.DEBUG if parsed.verbose else logging.WARNING
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=level)
    logger.setLevel(level)

    if not Path(parsed.file).exists():
        logger.error("找不到檔案：%s", parsed.file)
        sys.exit(1)

    urls = parse_urls(parsed.file)
    output_dir = Path(parsed.output)

    for url in urls:
        if not is_valid_youtube_url(url):
            logger.warning("略過無效 URL：%s", url)
            continue
        logger.info("下載中：%s", url)
        print(f"下載中：{url}")
        download_audio(url, output_dir)

    print("完成。")


if __name__ == "__main__":
    main()

import argparse
import re
import subprocess
import sys
from pathlib import Path

YOUTUBE_PATTERN = re.compile(
    r"https?://(www\.)?(youtube\.com/(watch\?.*v=|playlist\?.*list=)|youtu\.be/)\S+"
)


def is_valid_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_PATTERN.match(url))


def parse_urls(file_path: str) -> list:
    lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def download_audio(url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        url,
    ]
    subprocess.run(cmd, check=True)


def main(args=None):
    parser = argparse.ArgumentParser(description="批次下載 YouTube 音訊並轉為 MP3")
    parser.add_argument("file", help="包含 YouTube URL 的純文字檔")
    parser.add_argument("-o", "--output", default="output", help="輸出目錄（預設：output）")
    parsed = parser.parse_args(args)

    if not Path(parsed.file).exists():
        print(f"錯誤：找不到檔案 {parsed.file}", file=sys.stderr)
        sys.exit(1)

    urls = parse_urls(parsed.file)
    output_dir = Path(parsed.output)

    for url in urls:
        if not is_valid_youtube_url(url):
            print(f"略過無效 URL：{url}", file=sys.stderr)
            continue
        print(f"下載中：{url}")
        download_audio(url, output_dir)

    print("完成。")


if __name__ == "__main__":
    main()

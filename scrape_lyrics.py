#!/usr/bin/env python3
"""從 KKBOX 爬取蔡振南歌詞（繁體中文），不足時用網易雲備援（簡轉繁），輸出 lyrics.json"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
import opencc

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9",
}
NETEASE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://music.163.com/",
}

S2TW = opencc.OpenCC("s2tw")
KKBOX_BASE = "https://www.kkbox.com"
ARTIST = "蔡振南"

# 純演奏曲，無歌詞
INSTRUMENTAL = {
    "人",
    "煙花情 (交響樂團演奏曲)",
    "憨阿呆 (交響樂團演奏曲)",
}

ALBUMS = {
    "南歌": [
        "異鄉悲戀夢", "Change Change Change", "空笑夢", "大節女",
        "Lantern of Missing", "Money", "Mind Returning",
        "金包銀", "牛郎織女", "Night Missing You",
    ],
    "生命的太陽": [
        "生命的太陽", "Tai Tou Yi Xia Kan", "Ye Mei Gui",
        "Mother's Name Is Taiwan", "Yi Zhi Niao Zai Xiao Jiu Jiu",
        "Yi Zhi Yao Tao", "Liu Lang Tian Ya Ban Ji Ta",
        "Zui Hou De Tan Pan", "Fang Lang Ren Sheng",
        "Hei Yin Tian", "The Song of Wandering",
    ],
    "可愛可恨": [
        "甭擱憨", "Autumn Wind, Women Hearts", "福氣是命免人獒",
        "可愛可恨", "黃昏的故鄉", "Desolated", "What Is Called Love",
        "Lovesick", "Men's Heart", "港邊惜別",
    ],
    "8點檔連續劇主題曲 第二輯": [
        "煙花情", "憨阿呆", "春花夢露", "心酸酸", "碎心花",
        "失婚的女人", "金針花", "人",
        "煙花情 (交響樂團演奏曲)", "憨阿呆 (交響樂團演奏曲)",
    ],
    "無償": ["無償"],
}

TITLE_MAP = {
    "Change Change Change": "變變變",
    "Lantern of Missing": "相思燈",
    "Money": "錢",
    "Mind Returning": "回心轉意",
    "Night Missing You": "相思瞑",
    "Tai Tou Yi Xia Kan": "抬頭一下看",
    "Ye Mei Gui": "野玫瑰",
    "Mother's Name Is Taiwan": "母親的名字叫台灣",
    "Yi Zhi Niao Zai Xiao Jiu Jiu": "一隻鳥仔哮啾啾",
    "Yi Zhi Yao Tao": "一枝搖桃",
    "Liu Lang Tian Ya Ban Ji Ta": "流浪天涯伴吉他",
    "Zui Hou De Tan Pan": "最後的談判",
    "Fang Lang Ren Sheng": "放浪人生",
    "Hei Yin Tian": "黑陰天",
    "The Song of Wandering": "流浪之歌",
    "Autumn Wind, Women Hearts": "秋風女人心",
    "Desolated": "淒涼固定的",
    "What Is Called Love": "什麼號做愛",
    "Lovesick": "病相思",
    "Men's Heart": "查甫人的心",
}


# ── KKBOX ──────────────────────────────────────────

def kkbox_search_url(query: str) -> str | None:
    try:
        r = requests.get(
            f"{KKBOX_BASE}/tw/tc/search",
            params={"q": query}, headers=HEADERS, timeout=10,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if re.search(r"/tw/tc/song/\w+", a["href"]):
                href = a["href"]
                return KKBOX_BASE + href if href.startswith("/") else href
    except Exception:
        pass
    return None


def kkbox_lyrics(page_url: str) -> str | None:
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.select_one("div.lyrics")
        if div:
            text = div.get_text("\n").strip()
            if len(text) > 30:
                return text
    except Exception:
        pass
    return None


def fetch_from_kkbox(song: str) -> str | None:
    # 先用「藝人 + 歌名」搜
    url = kkbox_search_url(f"{ARTIST} {song}")
    if url:
        lyrics = kkbox_lyrics(url)
        if lyrics:
            return lyrics
    time.sleep(0.8)
    # fallback：只搜歌名
    url = kkbox_search_url(song)
    if url:
        lyrics = kkbox_lyrics(url)
        if lyrics:
            return lyrics
    return None


# ── 網易雲音樂（備援）──────────────────────────────

def netease_search_id(song: str) -> int | None:
    try:
        r = requests.get(
            "https://music.163.com/api/search/get",
            params={"s": f"{ARTIST} {song}", "type": 1, "limit": 3},
            headers=NETEASE_HEADERS, timeout=10,
        )
        songs = r.json().get("result", {}).get("songs", [])
        if songs:
            return songs[0]["id"]
    except Exception:
        pass
    return None


def netease_lyrics(song_id: int) -> str | None:
    try:
        r = requests.get(
            "https://music.163.com/api/song/lyric",
            params={"id": song_id, "lv": 1, "kv": 1, "tv": -1},
            headers=NETEASE_HEADERS, timeout=10,
        )
        raw = r.json().get("lrc", {}).get("lyric", "")
        if not raw:
            return None
        # 去掉 LRC 時間標記 [mm:ss.xx]
        lines = []
        for line in raw.splitlines():
            text = re.sub(r"\[\d+:\d+\.\d+\]", "", line).strip()
            if text and not text.startswith("作詞") and not text.startswith("作曲"):
                lines.append(text)
        result = "\n".join(lines).strip()
        if len(result) > 30:
            return S2TW.convert(result)
    except Exception:
        pass
    return None


def fetch_from_netease(song: str) -> str | None:
    song_id = netease_search_id(song)
    if song_id:
        return netease_lyrics(song_id)
    return None


# ── 主流程 ─────────────────────────────────────────

def main():
    result = {}

    for album, songs in ALBUMS.items():
        print(f"\n[專輯] {album}")
        result[album] = {}

        for song in songs:
            search_title = TITLE_MAP.get(song, song)
            label = f"{song} → {search_title}" if search_title != song else song
            print(f"  {label} ...", end=" ", flush=True)

            # 純演奏曲
            if search_title in INSTRUMENTAL or song in INSTRUMENTAL:
                print("♪ 純音樂")
                result[album][song] = "__instrumental__"
                continue

            # 1. KKBOX（含 fallback 只搜歌名）
            lyrics = fetch_from_kkbox(search_title)
            if lyrics:
                print(f"✓ KKBOX ({len(lyrics)} 字)")
                result[album][song] = lyrics
                time.sleep(1.0)
                continue

            time.sleep(0.8)

            # 2. 網易雲備援（簡轉繁）
            lyrics = fetch_from_netease(search_title)
            if lyrics:
                print(f"✓ 網易 ({len(lyrics)} 字)")
                result[album][song] = lyrics
                time.sleep(1.0)
                continue

            print("❌ 找不到")
            result[album][song] = None
            time.sleep(0.8)

    with open("lyrics.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = sum(1 for a in result.values() for v in a.values() if v)
    all_songs = sum(len(a) for a in result.values())
    print(f"\n完成：{total}/{all_songs} 首有結果 → lyrics.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""將 lyrics.json 組合成單一離線 lyrics.html"""

import json, html

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

with open("lyrics.json", encoding="utf-8") as f:
    raw = json.load(f)

# 整理：key 改為中文顯示名
albums = {}
for album, songs in raw.items():
    albums[album] = {}
    for song, lyrics in songs.items():
        display = TITLE_MAP.get(song, song)
        albums[album][display] = lyrics  # None 表示歌詞未收錄

# 建立 JS 資料結構
js_data = json.dumps(albums, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>阿嬤歌詞本</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
  body {{
    font-family: "Noto Sans TC", "PingFang TC", "微軟正黑體", sans-serif;
    background: #1a1a2e;
    color: #f0e6d3;
    min-height: 100vh;
    font-size: 18px;
  }}

  /* ── Header ── */
  #header {{
    background: #16213e;
    padding: 16px 16px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 3px solid #e94560;
    position: sticky;
    top: 0;
    z-index: 10;
  }}
  #back-btn {{
    background: #e94560;
    color: #fff;
    border: none;
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 1.3rem;
    font-weight: bold;
    cursor: pointer;
    display: none;
    min-width: 80px;
    touch-action: manipulation;
  }}
  #back-btn:active {{ background: #c73652; transform: scale(0.96); }}
  #page-title {{
    font-size: 1.4rem;
    font-weight: bold;
    color: #f0e6d3;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  /* ── Content wrapper ── */
  #content {{
    padding: 20px 14px 40px;
    max-width: 680px;
    margin: 0 auto;
  }}

  /* ── Button grid ── */
  .btn-grid {{
    display: grid;
    gap: 14px;
    /* 手機預設單欄，寬螢幕雙欄 */
    grid-template-columns: 1fr;
  }}
  @media (min-width: 480px) {{
    .btn-grid {{ grid-template-columns: 1fr 1fr; }}
  }}

  .btn {{
    background: #16213e;
    border: 2px solid #0f3460;
    border-radius: 20px;
    color: #f0e6d3;
    font-size: 1.5rem;
    font-weight: bold;
    /* 高度夠大，手指好按 */
    min-height: 90px;
    padding: 22px 16px;
    cursor: pointer;
    text-align: center;
    line-height: 1.45;
    word-break: break-all;
    touch-action: manipulation;
    width: 100%;
  }}
  .btn:active {{
    background: #0f3460;
    border-color: #e94560;
    transform: scale(0.97);
  }}
  .btn.no-lyrics {{
    opacity: 0.4;
    border-style: dashed;
    cursor: default;
  }}
  .btn.no-lyrics::after {{
    content: "\\A暫無歌詞，歡迎您投稿！";
    white-space: pre;
    font-size: 0.9rem;
    font-weight: normal;
    color: #999;
  }}

  /* ── Lyrics ── */
  #lyrics-view {{
    font-size: 1.5rem;
    line-height: 2.2;
    white-space: pre-wrap;
    background: #16213e;
    border-radius: 18px;
    padding: 24px 20px;
    border: 2px solid #0f3460;
  }}
  #lyrics-view .meta {{
    font-size: 1rem;
    color: #aaa;
    margin-bottom: 20px;
    line-height: 1.9;
    border-bottom: 1px solid #0f3460;
    padding-bottom: 14px;
  }}

  /* ── 手機橫向：歌詞縮小一點好捲動 ── */
  @media (max-height: 500px) and (orientation: landscape) {{
    #lyrics-view {{ font-size: 1.2rem; line-height: 1.9; }}
  }}
</style>
</head>
<body>

<div id="header">
  <button id="back-btn" onclick="goBack()">◀ 返回</button>
  <div id="page-title">🎵 阿嬤歌詞本</div>
</div>

<div id="content"></div>

<script>
const DATA = {js_data};

let stack = [];  // [{{ view, title }}]

function render(el, title) {{
  document.getElementById("page-title").textContent = title;
  document.getElementById("back-btn").style.display = stack.length ? "block" : "none";
  const content = document.getElementById("content");
  content.innerHTML = "";
  if (typeof el === "string") {{
    content.innerHTML = el;
  }} else {{
    content.appendChild(el);
  }}
  window.scrollTo(0, 0);
}}

function showAlbums() {{
  stack = [];
  const grid = document.createElement("div");
  grid.className = "btn-grid";
  for (const album of Object.keys(DATA)) {{
    const btn = document.createElement("button");
    btn.className = "btn";
    btn.textContent = album;
    btn.onclick = () => showSongs(album);
    grid.appendChild(btn);
  }}
  render(grid, "🎵 阿嬤歌詞本");
  document.getElementById("back-btn").style.display = "none";
}}

function showSongs(album) {{
  stack.push({{ fn: showAlbums, title: "🎵 阿嬤歌詞本" }});
  const songs = DATA[album];
  const grid = document.createElement("div");
  grid.className = "btn-grid";
  for (const [song, lyrics] of Object.entries(songs)) {{
    const btn = document.createElement("button");
    const isInstrumental = lyrics === "__instrumental__";
    const hasLyrics = lyrics && !isInstrumental;
    btn.className = "btn" + (hasLyrics ? "" : " no-lyrics");
    if (isInstrumental) {{
      btn.innerHTML = song + '<span style="display:block;font-size:0.9rem;font-weight:normal;color:#aaa;margin-top:6px">♪ 純音樂，無歌詞</span>';
    }} else {{
      btn.textContent = song;
    }}
    if (hasLyrics) btn.onclick = () => showLyrics(album, song, lyrics);
    grid.appendChild(btn);
  }}
  render(grid, album);
}}

function showLyrics(album, song, lyrics) {{
  stack.push({{ fn: () => showSongs(album), title: album }});
  // 分離 作詞/作曲 meta 與歌詞本文
  const lines = lyrics.split("\\n");
  let metaLines = [], bodyLines = [], metaDone = false;
  for (const line of lines) {{
    if (!metaDone && (line.includes("作詞") || line.includes("作曲") || line.trim() === "")) {{
      if (line.trim()) metaLines.push(line.trim());
    }} else {{
      metaDone = true;
      bodyLines.push(line);
    }}
  }}
  const meta = metaLines.length ? `<div class="meta">${{metaLines.join("<br>")}}</div>` : "";
  const body = bodyLines.join("\\n").trim();
  const div = `<div id="lyrics-view">${{meta}}${{escHtml(body)}}</div>`;
  render(div, song);
}}

function escHtml(s) {{
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}}

function goBack() {{
  const prev = stack.pop();
  if (prev) prev.fn();
}}

showAlbums();
</script>
</body>
</html>"""

with open("lyrics.html", "w", encoding="utf-8") as f:
    f.write(HTML)

total = sum(1 for songs in albums.values() for v in songs.values() if v)
all_songs = sum(len(s) for s in albums.values())
print(f"lyrics.html 生成完成（{total}/{all_songs} 首有歌詞）")

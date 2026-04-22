# YT2MP3-Batch Agent

## 目標
一個 CLI 工具，可批次下載 YouTube 影片音訊並轉換成 MP3 格式，支援階層式目錄結構。

## KISS 設計原則
- 單一 Python 腳本（`yt2mp3.py`）— 不使用框架，不需設定檔
- 輸入：單一 `.txt` 檔，或含多個 `urls.txt` 的目錄樹
- 輸出：MP3 檔案儲存至 `./output/`，自動鏡像 input 目錄結構
- 依賴：`yt-dlp` + `ffmpeg`（外部執行檔，非 Python wrapper）
- 無資料庫、無狀態、無常駐程式 — 執行即結束

## 使用方式
```bash
python3 yt2mp3.py input/               # 目錄模式，鏡像結構至 output/
python3 yt2mp3.py urls.txt             # 單一檔案模式
python3 yt2mp3.py input/ -o ~/Music   # 指定輸出目錄
python3 yt2mp3.py input/ -v           # 顯示除錯 log
```

## 目錄結構範例
```
input/                    output/
  music/urls.txt    →       music/*.mp3
  podcast/urls.txt  →       podcast/*.mp3
  lo-fi/urls.txt    →       lo-fi/*.mp3
```

## 架構
```
yt2mp3.py
├── is_valid_youtube_url(url) -> bool              # 驗證 URL 格式（含播放清單）
├── parse_urls(file_path) -> list[str]             # 讀取並過濾 URL 行
├── collect_url_files(input_dir) -> list[tuple]    # 遞迴收集 .txt，回傳 (絕對路徑, 相對路徑)
├── download_audio(url, output_dir) -> None        # 呼叫 yt-dlp subprocess
└── main(args)                                     # CLI 進入點，支援檔案或目錄輸入
```

## 支援的 URL 格式
| 類型 | 範例 |
|------|------|
| 單一影片 | `https://www.youtube.com/watch?v=XXXXXXXXXXX` |
| 短網址 | `https://youtu.be/XXXXXXXXXXX` |
| 播放清單 | `https://www.youtube.com/playlist?list=XXXXXXXXXXX` |
| 影片含播放清單 | `https://www.youtube.com/watch?v=XXX&list=XXX` |

## 依賴套件
- `yt-dlp` — 下載最佳音訊串流，自動展開播放清單（透過 venv 安裝，不污染系統）
- `ffmpeg` — yt-dlp 內部使用，負責 MP3 轉換（需系統安裝：`brew install ffmpeg`）
- 僅使用 Python 標準庫（subprocess、pathlib、argparse、re、logging）

## 環境設置
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

執行腳本時需在 venv 啟動狀態下，或直接使用 `.venv/bin/python3 yt2mp3.py`。

## TDD 計畫（Red → Green）

### 測試清單
| 測試名稱 | 驗證內容 |
|----------|----------|
| `test_parse_urls_valid` | 從檔案正確回傳 URL 列表 |
| `test_parse_urls_skips_blanks_and_comments` | 忽略空行與 `#` 開頭的註解 |
| `test_is_valid_youtube_url_accepts_standard` | `youtube.com/watch?v=` → True |
| `test_is_valid_youtube_url_accepts_short` | `youtu.be/` → True |
| `test_is_valid_youtube_url_accepts_playlist` | `youtube.com/playlist?list=` → True |
| `test_is_valid_youtube_url_accepts_video_with_list` | `watch?v=XXX&list=XXX` → True |
| `test_is_valid_youtube_url_rejects_other` | 非 YouTube 網址 → False |
| `test_download_audio_calls_yt_dlp` | subprocess 以正確參數呼叫（mock） |
| `test_download_audio_creates_output_dir` | 輸出目錄不存在時自動建立（mock） |
| `test_verbose_flag_sets_debug_logging` | `-v` 時 logging level 為 DEBUG |
| `test_default_logging_is_warning` | 無 `-v` 時 level 為 WARNING |
| `test_collect_url_files_from_dir` | 遞迴找出目錄內所有 `.txt`，回傳相對路徑 |
| `test_output_mirrors_input_structure` | input 子目錄結構在 output 中被正確建立 |
| `test_main_exits_on_missing_file` | 輸入路徑不存在時呼叫 sys.exit |

### 限制條件
- 每個函式必須可獨立測試（邏輯與副作用分離）
- `download_audio` 必須可被 mock — subprocess 呼叫隔離，測試不需要網路
- 執行測試套件時不需要任何網路連線

---

## 待辦：阿嬤歌詞查詞頁

### 背景
阿嬤的 Android 手機沒有網路，只有離線 MP3。她想看歌詞但不會打字，需要全按鈕操作介面。

### 決策
做成**單一離線 HTML 檔案**，無需安裝任何 app，瀏覽器開啟即用。

### 使用者需求
- 不能有任何文字輸入框
- 按歌手分類 → 點歌手 → 看該歌手歌曲列表 → 點歌曲 → 看歌詞
- 字體要大，按鈕要大（老人家友善）
- 完全離線，所有歌詞內嵌在 HTML 內

### 待辦清單
- [ ] 爬蟲抓取歌詞（依 output/ 目錄的歌手/歌曲結構）
- [ ] 將歌詞資料整理成 JSON 結構（`{ 歌手: { 歌曲: 歌詞 } }`）
- [ ] 製作 `lyrics.html`：歌手按鈕頁 → 歌曲按鈕頁 → 歌詞頁，三層導覽
- [ ] 大字體、高對比、返回按鈕
- [ ] 用 ADB 或 USB 傳入手機

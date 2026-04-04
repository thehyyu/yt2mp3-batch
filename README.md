# YT2MP3-Batch

批次下載 YouTube 影片音訊並轉換為 MP3 的 CLI 工具。

## 系統需求

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/)（用於音訊轉換）

```bash
brew install ffmpeg
```

## 安裝

```bash
git clone https://github.com/thehyyu/yt2mp3-batch.git
cd yt2mp3-batch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用方式

建立一個純文字檔，每行填入一個 YouTube URL：

```
# urls.txt
https://www.youtube.com/watch?v=XXXXXXXXXXX
https://youtu.be/XXXXXXXXXXX
https://www.youtube.com/playlist?list=XXXXXXXXXXX
```

`#` 開頭的行會被忽略（可當作註解）。

執行下載：

```bash
python3 yt2mp3.py urls.txt
```

MP3 檔案會儲存至 `./output/` 目錄。

## 選項

| 選項 | 說明 |
|------|------|
| `-o DIR` | 指定輸出目錄（預設：`./output`） |
| `-v` | 顯示除錯 log |

```bash
python3 yt2mp3.py urls.txt -o ~/Music
python3 yt2mp3.py urls.txt -v
```

## 支援的 URL 格式

| 類型 | 範例 |
|------|------|
| 單一影片 | `https://www.youtube.com/watch?v=...` |
| 短網址 | `https://youtu.be/...` |
| 播放清單 | `https://www.youtube.com/playlist?list=...` |
| 影片含播放清單 | `https://www.youtube.com/watch?v=...&list=...` |

## 執行測試

```bash
source .venv/bin/activate
pip install pytest
pytest test_yt2mp3.py -v
```

# HSI Strategy App

一個用於分析恆生指數的策略平台。

## 功能特色

- 技術指標計算（布林帶、MACD、RSI）
- Redis 快取機制，提升計算效能
- FastAPI 後端 API 服務

## 安裝與設定

### 環境需求

- Python 3.7+
- Redis 伺服器

### 安裝步驟

1. 複製專案

   ```bash
   git clone [倉庫地址]
   cd hsi-strategy-app
   ```

2. 安裝相依套件

   ```bash
   pip install -r requirements.txt
   ```

3. 環境變數設定

   ```bash
   cp .env.template .env
   ```

   根據需要修改 `.env` 檔案中的設定：

   - `REDIS_HOST`: Redis 伺服器主機位址（預設: localhost）
   - `REDIS_PORT`: Redis 伺服器埠號（預設: 6379）
   - `CACHE_TTL_SECONDS`: 快取過期時間（秒）（預設: 300）

4. 啟動伺服器

   ```bash
   cd backend
   python main.py
   ```

## API 文檔

伺服器啟動後，可訪問 <http://localhost:8000/docs> 查看完整 API 文檔。

### 主要 API 端點

- `/ping`: 健康檢查
- `/api/indicators/bollinger`: 布林帶指標
- `/api/indicators/macd`: MACD 指標
- `/api/indicators/rsi`: RSI 指標

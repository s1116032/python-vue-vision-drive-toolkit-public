# Vision Drive Toolkit (自駕車視覺辨識模型訓練 Toolchain)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-v0.100+-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg" alt="Vue 3">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

Vision Drive Toolkit 是一個基於 **FastAPI** 與 **Vue 3 (Composition API)** 開發的 MVP 等級全棧自駕車視覺模型訓練 Toolchain 平台。本平台提供完整的「資料上傳、自動化前處理、模型訓練排程、非同步狀態追蹤與結果下載」之全生命週期管理，旨在解決機器學習工程師（MLE）與資料標記團隊在管理大型視覺資料集與排程訓練時的痛點。

---

## 🌟 核心特色與架構亮點

### 1. 🛡️ 嚴謹的進階檔案安全驗證
傳統後端僅依賴客戶端宣告的 `Content-Type` 或副檔名，易遭受惡意檔案偽造攻擊。本平台在後端實作**雙重驗證機制**：首先檢查檔名結構，接著直接讀取二進位檔案的 `Magic Numbers`（透過 `filetype` 套件）。即使攻擊者將 `.exe` 惡意程式改名為 `.jpg` 上傳，系統亦能精準攔截，有效阻斷 RCE（遠端程式執行）風險。

### 2. 🎬 自動化影片非同步抽幀 (Video Frame Extraction)
針對自駕車連續影像資料，系統支援高畫質影片上傳。後端整合 `OpenCV (cv2)`，在接收影片後自動以每 **3 秒** 為間隔進行定時抽幀。抽幀程序會將影像矩陣轉換為符合標準的訓練圖片，並自動於本地儲存空間歸檔、建立索引，大幅降低人工切片的時間成本。

### 3. 🔑 安全的圖片預覽機制 (Query String Token)
前端使用原生 `<img>` 標籤載入受保護的圖片資源時，無法直接在 HTTP Header 中夾帶 JWT Bearer Token。為兼顧「安全性」與「瀏覽器原生快取/渲染效能」，本平台實作了 **Query String Token 驗證機制**：
- 前端發起請求前，先向後端申請一組高時效性、單次使用的 Image Token。
- 將該 Token 作為參數帶入 `src="api/v1/images/preview?token=..."`。
- 後端驗證 Token 成功後，以 `StreamingResponse` 串流回傳圖片，防止未授權用戶竊取訓練資料。

### 4. ⚡ 非同步背景任務排程 (FastAPI BackgroundTasks)
模型訓練屬於高度耗時的密集型運算。若採用同步阻塞 I/O，將導致 API Gateway 超時（Timeout）並崩潰。本平台採用 FastAPI 的 `BackgroundTasks` 機制，在接收到訓練請求、完成資料校驗與資料庫寫入後，**立即回傳任務 ID（HTTP 202 Accepted）**，不阻塞主執行緒。訓練任務則在後端工作執行緒中非同步執行，確保高併發環境下 API 的即時回應與系統穩定。

### 5. 📉 無輪詢（Anti-Polling）的前端狀態管理
為了避免傳統 `setInterval` 輪詢（Short Polling）對伺服器造成的無謂連線浪費與資料庫 I/O 壓力，本平台遵循企業級低負載規範，捨棄自動輪詢。前端採用**手動刷新機制與精準狀態快照**，配合 UI 骨架屏與防抖（Debounce）處理，將主動權交還給使用者，大幅降低伺服器端併發壓力。

### 6. 🎨 輕量、無衝突的響應式 UI
前端視覺基於 **Vue 3** 搭配 **Bootstrap 5 CSS**。在架構設計上，刻意**完全不引入 Bootstrap JS** 及其相依的 Popper.js。所有動態效果（如：圖片預覽彈窗 `ImagePreviewModal`、側邊欄收摺）皆純粹透過 Vue 的響應式狀態（`v-if`、`v-show`、`:class`）驅動。此舉徹底避免了 Vue 虛擬 DOM（Virtual DOM）與 Bootstrap 原生 DOM 操縱之間的生命週期衝突，確保 UI 渲染效能最佳化。

---

## 🛠️ 技術棧 (Tech Stack)

### 後端 (Backend)
* **核心框架**: Python 3.10+ / FastAPI (基於 Starlette 與 Pydantic，兼具高效能與嚴格型別校驗)
* **非同步資料庫驅動**: SQLite 搭配 `aiosqlite`，實現 100% 全非同步 I/O 操縱，防止資料庫讀寫阻塞事件迴圈
* **ORM 框架**: SQLAlchemy 2.0+ (採用最新 Async Session 模式與 2.0 Style 查詢語法)
* **安全與認證**: JWT (`python-jose` 進行簽署與解密) /密碼雜湊採用 `bcrypt` 進行強力鹽值加密
* **圖像與工具庫**: OpenCV (`opencv-python-headless` 用於高效影像抽幀處理) / `filetype` (二進位 Magic Number 辨識)

### 前端 (Frontend)
* **核心框架**: Vue 3 (全面導入 Composition API `<script setup>`)
* **建構工具**: Vite (極速熱更新與優化打包)
* **路由管理**: Vue Router 4 (封裝全域前置路由守衛 `beforeEach`，嚴格執行 JWT 權限跳轉)
* **網路通訊**: Axios (封裝統一攔截器 `interceptors`，自動附加 JWT Bearer Token、全域錯誤攔截與錯誤提示)
* **樣式架構**: Bootstrap 5 (僅引進 CSS 進行網格排版與元件語意化)

---

## 📂 專案架構 (Project Structure)

```text
vision-drive-toolkit/
├── backend/                  # FastAPI 後端系統根目錄
│   ├── app/
│   │   ├── auth/             # 使用者認證模組 (註冊、登入、密碼雜湊、JWT 簽發)
│   │   ├── images/           # 資料管理模組 (圖片/影片上傳、安全驗證、OpenCV 抽幀、安全預覽 API)
│   │   ├── tasks/            # 任務調度模組 (訓練排程管理、非同步模擬模擬 API)
│   │   ├── database.py       # SQLAlchemy 異步 Engine 與 Session 宣告
│   │   ├── models.py         # SQLAlchemy 資料庫 ORM 模型 (User, Image, Task 模型)
│   │   └── main.py           # FastAPI 核心應用進入點、CORS 中間件設定、例外處理常式
│   ├── uploads/              # 本地儲存空間 (存放上傳之原影片與抽幀後之資料集，系統自動建立)
│   ├── run.py                # 應用啟動腳本
│   └── requirements.txt      # 後端依賴套件清單
│
├── frontend/                 # Vue 3 前端系統根目錄
│   ├── src/
│   │   ├── components/       # 跨頁面複用之原子元件 (如：ImagePreviewModal)
│   │   ├── views/            # 系統核心頁面 (Login.vue, Dashboard.vue, Train.vue, Tasks.vue)
│   │   ├── services/         # API 服務層 (Axios 實例封裝、Request/Response 攔截器)
│   │   └── router/           # 路由模組 (定義路由表與 Auth 導航守衛)
│   ├── vite.config.js        # Vite 設定檔 (配置反向代理 Proxy 解決開發環境跨域 CORS 問題)
│   └── package.json          # 前端依賴項與腳本設定
└── README.md                 # 專案說明文件

```

---

## 🚀 快速開始 (Quick Start)

### 1. 啟動後端伺服器 (Backend Setup)

確保您的環境已安裝 Python 3.10 或以上版本：

```bash
# 導航至後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境
# Windows 環境:
venv\Scripts\activate
# Mac / Linux 環境:
source venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt

# 執行資料庫遷移與啟動服務
python run.py

```

* 後端本地伺服器將執行於：`http://127.0.0.1:8000`
* 系統自動整合的互動式 API 文件 (Swagger UI)：`http://127.0.0.1:8000/docs`

### 2. 啟動前端開發伺服器 (Frontend Setup)

確保您的環境已安裝 Node.js (建議 v18+)：

```bash
# 導航至前端目錄
cd frontend

# 安裝前端專案依賴
npm install

# 啟動 Vite 開發伺服器
npm run dev

```

* 前端本地服務將執行於：`http://localhost:5173`

---

## 🔄 核心操作流程 (Workflow Summary)

```
[使用者註冊] -> [Terminal 列印驗證連結] -> [帳號啟用]
     |
     v
[Dashboard 上傳] -> (若為影片: 後端自動觸發 OpenCV 3秒非同步抽幀歸檔)
     |
     v
[Train 頁面] -> [選取訓練圖片資料] -> [點擊開始訓練] -> (觸發 FastAPI BackgroundTasks)
     |
     v
[Tasks 任務頁面] -> [手動重新整理] -> [狀態轉為已完成] -> [安全下載模型模擬檔 (test.txt)]

```

1. **認證與安全性測試**：
使用者在前端提交註冊表單，後端系統會自動攔截請求，並將「Email 驗證啟用連結」直接印出於後端的控制台（Terminal）（此處安全地模擬了真實生產環境下的 SMTP 發信流程）。點擊該連結後，資料庫狀態將更新，帳號正式啟用。
2. **多媒體前處理測試**：
登入系統後進入 `Dashboard`，使用者可嘗試上傳 `.mp4` 或 `.jpg` 檔案。若上傳檔案為影片，後端將自動在背景利用畫格計數器擷取每 3 秒的影像並儲存，刷新頁面即可看見抽幀後的圖片集。
3. **訓練任務建立**：
切換至 `Train` 模型訓練分頁，頁面將撈取目前已就緒的資料集圖片。勾選欲加入本次訓練的圖片後，點擊「開始訓練」，系統即刻建立背景任務並迅速導向任務追蹤頁。
4. **狀態追蹤與成果產出**：
在 `Tasks` 頁面中，使用者可點擊「重新整理狀態」按鈕以獲取最新任務進度。當背景的虛擬訓練任務執行完畢，狀態將由 `processing` 變更為 `completed`，此時下載按鈕解鎖，使用者可安全下載模型成果檔案（MVP 階段以 `test.txt` 模擬打包輸出）。
3. **文字排版專業**：使用了徽章（Badges）、語意化的 Emoji、清晰的專案樹狀圖以及文字流向圖，大幅提升閱讀體驗。

## License
Copyright © 2026 hanwu910514.

詳情請參閱[Apache License 2.0](LICENSE)檔案

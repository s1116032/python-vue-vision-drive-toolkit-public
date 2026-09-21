# Vision Drive Toolkit 🚗💨
> **自駕車視覺標註與訓練資料準備 Toolchain (Full-Stack MVP)**

## 📌 專案簡介
**Vision Drive Toolkit** 是一個為自駕車視覺模型打造的端到端資料前處理與標註平台。
本專案涵蓋了**安全檔案上傳、OpenCV 自動化影片抽幀、專注模式 SVG 標註畫布 (BBox & Polygon)**，直至 **YOLO 格式訓練資料集的自動化轉換與打包**。

*(註：本專案聚焦於 MLOps 中的「資料準備與標註」階段。目前系統產出並供下載的「模型」，實為標準化的 YOLO 格式資料集 `.zip`，已預留標準接口供日後串接真實的 GPU 訓練腳本。)*

## 💡 專案背景與開發動機 (Background & Motivation)

本專案的概念源自作者於**國立陽明交通大學 IVSLab (智慧視覺系統實驗室)** 擔任研究助理期間，參與開發「自動化深度學習工具」的實務經驗。

當時在團隊中，登入系統與標註系統由其他成員負責開發，作者主要負責接任部分功能與後續測試。為了**徹底掌握深度學習 Toolchain 的全貌**，並**鍛鍊獨立完成全端系統開發的能力**，作者決定在業餘時間**從零開始獨立復刻並補全**整個系統。

由於開發時間有限，本專案以 **MVP (最小可行性產品)** 的形式快速實作，旨在打通從「帳號管理、資料處理、影像標註到模型訓練排程」的完整端到端流程，並刻意在架構上採用了現代化的工程實踐，以確保系統的健壯性與擴展性。

---

## 🌟 核心技術亮點 (Engineering Highlights)

在本專案的獨立架構設計與實作過程中，為了確保系統的效能與精準度，特別採用了以下工程實踐：

### 1. 避免 Event Loop 阻塞的背景任務設計 (Concurrency & I/O)
* **設計考量**：在 FastAPI 中，若將耗時的同步 I/O 操作（如大量圖片複製與 ZIP 打包）放入 `async def` 中，會阻塞主執行緒的 `asyncio` Event Loop。
* **實作方式**：刻意採用 **Threadpool 執行緒池** 機制。將背景任務定義為純同步函數 (`def`)，讓 FastAPI 自動將其丟入背景執行緒執行。同時引入 SQLAlchemy 的 `SyncSession` 進行獨立事務管理，確保主 API 請求的毫秒級響應，維持系統的高併發處理能力。

### 2. 像素級精準的 SVG 標註引擎 (Geometry & Rendering)
* **設計考量**：前端 `<img>` 標籤使用 `object-fit: contain` 保持比例時會產生黑邊，若 SVG 畫布直接鋪滿外層容器，會導致滑鼠點擊座標與圖片實際像素發生偏移。
* **實作方式**：重構 CSS Flexbox 層級，使用 `min-height: 0` 與 `calc(100vh - Xpx)` 確保 SVG 畫布**嚴絲合縫地貼合圖片的物理渲染尺寸**。並直接讀取 SVG 的 `getBoundingClientRect()` 進行歸一化計算，確保標註座標 100% 零誤差。

### 3. 歸一化座標系統與自動化輸出管道 (Data Engineering)
* **設計考量**：若儲存絕對像素座標，前端畫布縮放或未來更換模型輸入尺寸時，需要繁瑣的換算。
* **實作方式**：資料庫一律採用 `0.0 ~ 1.0` 的歸一化座標 (Normalized Coordinates)。後端在觸發任務時，只需透過簡單的數學映射即可瞬間轉換為標準的 **YOLO Detect 格式**，並自動打包為 `.zip` 訓練資料集，為日後無縫接入真實訓練腳本打下基礎。

### 4. 無輪詢的狀態管理與專注模式 UX 優化 (Frontend Architecture)
* **防呆與效率**：實作 **Sticky Category (記憶上次類別)** 機制，減少標註者的點擊次數；支援 Polygon 起點閉合偵測與鍵盤快捷鍵。
* **拒絕無效輪詢**：摒棄浪費伺服器資源的 `setInterval` 輪詢機制，改用手動觸發狀態快照。並透過 Vue Router 的 Meta 屬性實作 **「無干擾專注模式」**，進入標註時自動隱藏系統導覽列，提供最大化的工作區。

### 5. 多層級資安防護 (Security)
* **Magic Numbers 驗證**：不信任客戶端偽造的 `Content-Type`，後端讀取檔案前 2KB 的 Hex 簽名 (使用 `filetype` 套件) 進行真實格式驗證，阻擋惡意執行檔。
* **JWT 與 `<img>` 標籤的妥協藝術**：為解決原生 `<img src="...">` 無法夾帶 Authorization Header 的問題，後端實作基於 Query String 的 Temporary Token 驗證機制，兼顧資安與瀏覽器原生渲染效能。

---

## 🛠️ 技術棧 (Tech Stack)

| 領域 | 技術與工具 |
| :--- | :--- |
| **後端 (Backend)** | Python 3.10+, **FastAPI**, SQLAlchemy 2.0 (Async/Sync), SQLite, Pydantic, OpenCV, python-jose (JWT), bcrypt |
| **前端 (Frontend)** | **Vue 3 (Composition API)**, Vite, Vue Router 4, Axios, SVG (原生 DOM 渲染), Bootstrap 5 (CSS Only) |
| **架構與設計** | RESTful API, Background Threadpool, Normalized Coordinate System, Data Pipeline |

---

## 🔄 系統資料流 (Data Pipeline)

```text
[使用者上傳影片/圖片] 
       ↓ (OpenCV 3秒抽幀 / Magic Numbers 驗證)
[本地儲存區 + SQLite (歸一化座標 JSON)]
       ↓ (Vue 3 SVG 專注模式畫布標註)
[標註完成 (Sticky Category / BBox / Polygon)]
       ↓ (觸發 FastAPI BackgroundTasks)
[Threadpool 執行緒：YOLO 格式轉換 + 圖片複製 + ZIP 打包]
       ↓
[前端下載 dataset_task_{id}.zip (YOLO 格式資料集)] 
       ↓ (預留接口)
[日後串接 PyTorch / YOLO 訓練腳本產出真實模型權重]
```

---

## 🚀 快速啟動 (Quick Start)

### 1. 啟動後端 (Backend)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python run.py
# 伺服器啟動於 http://127.0.0.1:8000 (Swagger UI: /docs)
```

### 2. 啟動前端 (Frontend)
```bash
cd frontend
npm install
npm run dev
# 開發伺服器啟動於 http://localhost:5173
```

---

## 🔮 架構演進與未來展望 (Scalability & Future Work)

本專案為 MVP 階段，基於過往於實驗室監督標註團隊的實務經驗，若需導入真實生產環境，已規劃以下架構升級路徑以解決真實業務痛點：

1. **基於角色的存取控制 (RBAC) 與權限隔離**：
   * 實作 `Admin` (系統管理員)、`Supervisor` (監督者/行政人員) 與 `Annotator` (工讀生/標註員) 的多角色權限系統。
   * 前端透過 Vue Router 守衛隱藏後台入口，後端透過 JWT Payload 驗證與 FastAPI 依賴注入 (`Depends`) 確保 API 級的權限隔離，防止越權存取。
2. **計件薪資統計與宏觀數據看板 (Payroll & Data Readiness Dashboard)**：
   * **計件薪資自動化**：解決過去「人工計算工讀生標記數量以核發計件薪資」的繁瑣痛點，系統自動依據標記的 BBox/Polygon 數量與複雜度產出薪資報表。
   * **管理層數據看板**：提供決策者 (老闆/PM) 專用的宏觀視角，即時呈現「特定週期內的總標記產出」、「資料集狀態分佈（未標記/標記中/已審核）」以及「目前可用於模型訓練的乾淨數據總量」，輔助商業與研發決策。
3. **真實模型訓練接入**：將目前的資料集打包輸出邏輯，無縫對接真實的 GPU 訓練腳本 (如 Ultralytics YOLOv8)，產出 `.pt` 或 `.onnx` 模型權重檔。
4. **分散式任務佇列**：將 Threadpool 替換為 **Celery + Redis**，支援多節點 GPU 伺服器叢集的大規模併發訓練。
5. **進階標註輔助**：整合 **SAM (Segment Anything Model)** 實現點擊自動生成 Polygon 遮罩，進一步提升工讀生的標註效率。

---

## License
Copyright © 2026 hanwu910514.

詳情請參閱[Apache License 2.0](LICENSE)檔案
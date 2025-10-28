# api-ocr-2025

本專案為 OCR (Optical Character Recognition) API 模組，  
使用 TWCC LLM 模型進行收據 / 發票影像文字辨識與結構化資訊萃取。  
可獨立運作，或整合至醫療報銷系統、表單掃描平台等應用。

---

## 專案結構
```
api-ocr-2025/
├── ocr.py
├── requirements.txt
├── .env
├── LICENSE
├── README.md
└── prompt/
    └── ocr_prompt.txt
```

---

## 主要功能
- 提供 REST API 介面 (`/process_image_llm_twcc`)
- 可上傳收據 / 發票圖片（JPG、PNG）
- 由 TWCC LLM 模型分析影像文字內容
- 解析出發票號碼、日期、統編、營業人名稱、金額等欄位
- 結果以 JSON 格式回傳

---

## 安裝步驟

### 1. 下載專案
```bash
git clone https://github.com/xxx/api-ocr-2025.git
cd api-ocr-2025
```

### 2. 建立虛擬環境（建議）
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. 安裝依賴套件
```bash
pip install -r requirements.txt
```

---

## 設定環境變數

建立 `.env` 檔案於專案根目錄中：

```
# TWCC 雲端大型語言模型 (LLM) API
TWCC_LLM_API_URL=https://api-ams.twcc.ai/api/models
TWCC_API_KEY=你的_TWCC_API_KEY

# OpenAI API 金鑰（非必要）
OPENAI_API_KEY=你的_OPENAI_API_KEY

# FastAPI 伺服器設定
HOST=0.0.0.0
PORT=9099

# 可指定外部 Prompt 檔案路徑
OCR_PROMPT_FILE=prompt/ocr_prompt.txt
```

---

## 設定 OCR Prompt

請於 `prompt/ocr_prompt.txt` 放入辨識規則文字，例如：

```
以下是一張台灣的收據或發票照片，請依照以下規則進行分析：

1. 憑證判斷：
請先判斷該圖片是否屬於以下五種類型之一：
電子發票、二聯式發票、三聯式發票、免用統一發票收據、其他。
若無法判斷為上述任一種類，請回傳：
{"憑證格式":"其他","憑證號碼":"","憑證日期":"","隨機碼":"","賣方統編":"","賣方營業人名稱":"","金額":""}

2. 欄位抽取：
- 憑證號碼：AA-12345678 格式（兩碼英文+八碼數字）
- 憑證日期：轉換成 YYYY-MM-DD HH:mm:ss（民國需 +1911）
- 賣方統編：8 碼數字
- 賣方營業人名稱：公司或商店名稱
- 金額：純數字（不含貨幣符號與逗號）

若欄位不存在，請填空字串 ""。
回覆內容需為合法 JSON，禁止其他描述性文字。
```

> 可依實際需求修改辨識邏輯與格式

---

## 啟動服務
```bash
python ocr.py
```

或使用 Uvicorn：
```bash
uvicorn ocr:app --host 0.0.0.0 --port 9099
```

啟動後伺服器預設運行於：
```
http://localhost:9099
```

---

## API 使用說明

### Endpoint
```
POST /process_image_llm_twcc
```

### Request 格式
| 參數名稱 | 類型 | 必填 | 說明 |
|-----------|------|------|------|
| file | file | ✅ | 上傳的影像檔 (JPG / PNG) |
| Category | string | ❌ | 可選欄位，若未提供則自動使用 `"default"` |
| OCRPrompt | string | ❌ | 可覆寫預設辨識規則（不填則使用 `prompt/ocr_prompt.txt`） |

### Curl 範例
```bash
# 範例 1：最簡單的使用方式（不提供 Category）
curl -X POST "http://localhost:9099/process_image_llm_twcc"   -F "file=@sample.jpg"

# 範例 2：帶有分類欄位
curl -X POST "http://localhost:9099/process_image_llm_twcc"   -F "file=@sample.jpg"   -F "Category=test"
```

### 成功回傳範例
```json
[
  {
    "Result": "成功",
    "Item": {
      "憑證格式": "電子發票",
      "憑證號碼": "AB-12345678",
      "憑證日期": "2024-09-18 14:35:20",
      "隨機碼": "1234",
      "賣方統編": "12345678",
      "賣方營業人名稱": "諾歐科技股份有限公司",
      "金額": "550"
    },
    "Category": "test",
    "OCR": "TWCC"
  }
]
```

### 錯誤回傳範例
```json
[
  {
    "Result": "失敗",
    "Item": [],
    "Category": "default",
    "OCR": "TWCC"
  }
]
```

---

## 套件需求
已列於 `requirements.txt`：
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
google-cloud-vision>=3.7.4
google-api-core>=2.19.0
requests>=2.32.3
openai>=1.47.0
python-dotenv>=1.0.1
pydantic>=2.9.2
aiofiles>=23.2.1
python-multipart>=0.0.9
```

---

## 授權條款
本專案採用 MIT License。  
詳見 [LICENSE](./LICENSE)。

---

## 維運資訊
| 項目 | 負責人 |
|------|----------|
| 原始作者 | Andy Chang |
| 維運者 | Andy Chang |
| 聯絡信箱 | andy.chang@neov.ai |

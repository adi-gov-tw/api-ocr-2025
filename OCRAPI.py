from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import JSONResponse
from google.cloud import vision
from google.api_core.exceptions import GoogleAPICallError, RetryError
import requests, json, base64, os, logging, time, asyncio, uvicorn, io
from dotenv import load_dotenv
import openai
from PIL import Image
import torch
from transformers import MllamaForConditionalGeneration, AutoProcessor

# ------------------------------------------------------------
# 初始化設定
# ------------------------------------------------------------
load_dotenv()  # 載入 .env 檔案

# TWCC LLM API 設定
TWCC_LLM_API_URL = os.getenv("TWCC_LLM_API_URL", "https://api-ams.twcc.ai/api/models")
TWCC_API_KEY = os.getenv("TWCC_API_KEY")

# FastAPI 初始化
app = FastAPI()
logger = logging.getLogger("uvicorn.error")

# ------------------------------------------------------------
# 載入 OCR Prompt：優先使用外部文字檔，其次使用 .env
# ------------------------------------------------------------
PROMPT_FILE_PATH = os.getenv("OCR_PROMPT_FILE", "prompt/ocr_prompt.txt")
OCR_PROMPT = ""

if os.path.exists(PROMPT_FILE_PATH):
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            OCR_PROMPT = f.read()
            logger.info(f"OCR_PROMPT 已從檔案載入: {PROMPT_FILE_PATH}")
    except Exception as e:
        logger.error(f"無法讀取 OCR_PROMPT 檔案: {e}")
else:
    OCR_PROMPT = os.getenv("OCR_PROMPT", "")
    if OCR_PROMPT:
        logger.info("OCR_PROMPT 已從環境變數載入")
    else:
        logger.warning("未設定 OCR_PROMPT，請確認 prompt/ocr_prompt.txt 或 .env")

# ------------------------------------------------------------
# 安全檢查
# ------------------------------------------------------------
if not TWCC_API_KEY:
    raise RuntimeError("缺少 TWCC_API_KEY，請於 .env 或環境變數中設定")

# 初始化 TWCC API Client
client = openai.OpenAI(
    api_key=TWCC_API_KEY,
    base_url=TWCC_LLM_API_URL
)

# ------------------------------------------------------------
# Hugging Face Llama 3.2 Vision 模型設定
# ------------------------------------------------------------
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.2-11B-Vision-Instruct")
HF_ENABLED = os.getenv("HF_ENABLED", "false").lower() == "true"
hf_model = None
hf_processor = None

def load_hf_model():
    """延遲載入 Hugging Face 模型（首次呼叫時才載入）"""
    global hf_model, hf_processor
    if hf_model is None:
        logger.info(f">>> 正在載入 {HF_MODEL_ID} 模型...")
        hf_model = MllamaForConditionalGeneration.from_pretrained(
            HF_MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        hf_processor = AutoProcessor.from_pretrained(HF_MODEL_ID)
        logger.info(f">>> {HF_MODEL_ID} 模型載入完成")
    return hf_model, hf_processor

# ------------------------------------------------------------
# OCR 主端點
# ------------------------------------------------------------
@app.post("/process_image_llm_twcc")
async def process_image_llm_twcc(
    request: Request,
    file: UploadFile = File(...),
    Category: str = Form(None),
    OCRPrompt: str = Form(None)
):
    """
    使用 TWCC LLM 模型進行 OCR 發票/收據結構化辨識。
    可透過表單參數覆寫預設的 OCR_PROMPT。
    """
    try:
        logger.info(">>> process_image_llm_twcc 開始執行")
        t0 = time.perf_counter()

        # 1. 讀取上傳檔案
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # 2. 使用輸入的 Prompt 或預設 Prompt
        prompt = OCRPrompt or OCR_PROMPT

        if not prompt.strip():
            raise ValueError("OCR_PROMPT 為空，請確認 prompt/ocr_prompt.txt 或 .env 設定")

        # 3. 準備 LLM 訊息內容
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        # 4. 呼叫 TWCC 模型
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="llama3.2-ffm-11b-v-32k-chat",
                temperature=0.1,
                max_tokens=1600,
                top_p=0.1,
                messages=messages
            )
        )

        reply = response.choices[0].message.content
        cleaned = reply.strip().replace("```json", "").replace("```", "").replace("\n", "")

        # 5. 嘗試解析 JSON
        querySource = []
        try:
            result_json = json.loads(cleaned)
            querySource.append({
                "Result": "成功",
                "Item": result_json,
                "Category": Category,
                "OCR": "TWCC"
            })
        except json.JSONDecodeError:
            querySource.append({
                "Result": "失敗",
                "Item": [reply],
                "Category": Category,
                "OCR": "TWCC"
            })

        logger.info(">>> process_image_llm_twcc 執行完畢")
        return JSONResponse(content=querySource, status_code=200)

    except Exception as e:
        logger.error(f"例外發生: {e}")
        return JSONResponse(
            content=[{"Result": "失敗", "Item": [], "Category": Category, "OCR": "TWCC"}],
            status_code=500
        )


# ------------------------------------------------------------
# OCR 端點 - Hugging Face 本地模型
# ------------------------------------------------------------
@app.post("/process_image_llm_hf")
async def process_image_llm_hf(
    request: Request,
    file: UploadFile = File(...),
    Category: str = Form(None),
    OCRPrompt: str = Form(None)
):
    """
    使用本地 Hugging Face Llama-3.2-11B-Vision-Instruct 模型進行 OCR。
    需要先申請 Meta Llama 授權並登入 huggingface-cli。
    """
    try:
        logger.info(">>> process_image_llm_hf 開始執行")
        t0 = time.perf_counter()

        # 1. 載入模型（首次呼叫時）
        model, processor = load_hf_model()
        t_load = time.perf_counter()

        # 2. 讀取上傳檔案並轉換為 PIL Image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        t1 = time.perf_counter()

        # 3. 使用輸入的 Prompt 或預設 Prompt
        prompt = OCRPrompt or OCR_PROMPT
        if not prompt.strip():
            raise ValueError("OCR_PROMPT 為空，請確認 prompt/ocr_prompt.txt 或 .env 設定")

        # 4. 準備 Llama 3.2 Vision 格式的訊息
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(
            image,
            input_text,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)
        t2 = time.perf_counter()

        # 5. 執行推論
        loop = asyncio.get_running_loop()
        output = await loop.run_in_executor(
            None,
            lambda: model.generate(
                **inputs,
                max_new_tokens=1600,
                temperature=0.1,
                top_p=0.1,
                do_sample=True
            )
        )
        t3 = time.perf_counter()

        # 6. 解碼輸出
        reply = processor.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        cleaned = reply.strip().replace("```json", "").replace("```", "").replace("\n", "")

        logger.info(f"[分析時間] 模型載入: {(t_load - t0)*1000:.1f}ms, 讀檔: {(t1 - t_load)*1000:.1f}ms, 預處理: {(t2 - t1)*1000:.1f}ms, 推論: {(t3 - t2)*1000:.1f}ms")

        # 7. 嘗試解析 JSON
        querySource = []
        try:
            result_json = json.loads(cleaned)
            querySource.append({
                "Result": "成功",
                "Item": result_json,
                "Category": Category,
                "OCR": "HuggingFace"
            })
        except json.JSONDecodeError:
            querySource.append({
                "Result": "失敗",
                "Item": [reply],
                "Category": Category,
                "OCR": "HuggingFace"
            })

        logger.info(">>> process_image_llm_hf 執行完畢")
        return JSONResponse(content=querySource, status_code=200)

    except Exception as e:
        logger.error(f"process_image_llm_hf 例外發生: {e}")
        return JSONResponse(
            content=[{"Result": "失敗", "Item": [], "Category": Category, "OCR": "HuggingFace"}],
            status_code=500
        )


# ------------------------------------------------------------
# 主程式入口點
# ------------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 9099))
    uvicorn.run(app, host=host, port=port)

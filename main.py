import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

INTERNAL_SECRET = os.getenv("VORTEX_INTERNAL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
api_key_header = APIKeyHeader(name="X-Vortex-Auth")

class ChatRequest(BaseModel):
    message: str

async def verify_vortex_request(token: str = Depends(api_key_header)):
    if token != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Erişim Reddedildi")
    return token

# Hata ayıklama için yeni endpoint
@app.get("/api/v1/models")
async def list_models():
    # Mevcut API anahtarının erişebildiği modelleri listeler
    models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    return {"models": models}

@app.post("/api/v1/chat")
async def chat_with_gemini(request: ChatRequest, token: str = Depends(verify_vortex_request)):
    try:
        # Modeli burada çağırıyoruz
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(request.message)
        return {"response": response.text}
    except Exception as e:
        # Hata olursa hatanın ne olduğunu (500) direkt bize söylesin
        raise HTTPException(status_code=500, detail=str(e))
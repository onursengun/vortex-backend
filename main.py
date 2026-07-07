import os
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Annotated
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Ayarları: Emülatörden veya başka bir ağdan gelen istekleri engellememesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ortam değişkenlerini al
INTERNAL_SECRET = os.getenv("VORTEX_INTERNAL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API Key varsa sistemi yapılandır
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/v1/chat")
async def chat_with_gemini(
    request: ChatRequest, 
    x_vortex_auth: Annotated[str, Header(alias="X-Vortex-Auth")]
):
    # 1. Şifre Kontrolü
    if x_vortex_auth != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Erişim Reddedildi: Şifre Hatalı.")
    
    # 2. API Key Kontrolü
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Sunucu Hatası: GEMINI_API_KEY bulunamadı.")
    
    try:
        # 3. Garanti çalışan model ismi
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(request.message)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google API Hatası: {str(e)}")

@app.get("/")
async def root():
    if not GEMINI_API_KEY:
        return {"status": "Hata: API Key bulunamadı"}
    try:
        # Google'dan sana özel açık olan modellerin listesini çeker
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return {
            "status": "Vortex API is online!",
            "google_izin_verilen_modeller": models
        }
    except Exception as e:
        return {"status": "Sunucu çalışıyor ama Google'a bağlanamadı", "error": str(e)}
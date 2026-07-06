import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel

# .env dosyasındaki sırları yükler
load_dotenv()

app = FastAPI()

# Şifreleri çekiyoruz
INTERNAL_SECRET = os.getenv("VORTEX_INTERNAL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini'yi bu gizli şifreyle yapılandırıyoruz
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY .env dosyasında bulunamadı!")
genai.configure(api_key=GEMINI_API_KEY)

# Android'den gelecek "X-Vortex-Auth" başlığını bekliyoruz
api_key_header = APIKeyHeader(name="X-Vortex-Auth")

# Android'den gelecek isteğin (JSON) yapısı
class ChatRequest(BaseModel):
    message: str

# Güvenlik Kontrolü
async def verify_vortex_request(token: str = Depends(api_key_header)):
    if token != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Erişim Reddedildi: Geçersiz İstemci")
    return token

# Yapay Zeka Sohbet Uç Noktası
@app.post("/api/v1/chat")
async def chat_with_gemini(request: ChatRequest, token: str = Depends(verify_vortex_request)):
    try:
        # Gemini modelini seç
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Modele soruyu gönder
        response = model.generate_content(request.message)
        
        # Cevabı Android'e geri yolla
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
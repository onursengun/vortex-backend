import os
from fastapi import FastAPI, HTTPException, Header
import google.generativeai as genai
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

# Render'dan gelen güvenli ortam değişkenleri
INTERNAL_SECRET = os.getenv("VORTEX_INTERNAL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/v1/chat")
async def chat_with_gemini(
    request: ChatRequest, 
    # FastAPI'a header'ı okuması gerektiğini net bir şekilde söylüyoruz
    x_vortex_auth: Annotated[str, Header(alias="X-Vortex-Auth")]
):
    # Şifre kontrolü
    if x_vortex_auth != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Erişim Reddedildi")
    
    try:
        # Kota dostu ve stabil model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(request.message)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu Hatası: {str(e)}")

@app.get("/")
async def root():
    return {"status": "Vortex API is online and functional!"}
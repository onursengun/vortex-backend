import os
from fastapi import FastAPI, HTTPException
import google.generativeai as genai
from pydantic import BaseModel

app = FastAPI()

# Render'ın Environment kısmındaki değişkenleri direkt okur
INTERNAL_SECRET = os.getenv("VORTEX_INTERNAL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/v1/chat")
async def chat_with_gemini(request: ChatRequest, x_vortex_auth: str = None):
    # Şifre kontrolü
    if x_vortex_auth != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Erişim Reddedildi")
    
    try:
        # Kota dostu, en stabil model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(request.message)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "Vortex API is online!"}
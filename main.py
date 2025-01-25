from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import logging
import uuid
from typing import Dict
from models import Database
from agent import Agent
import asyncio
import os

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI()

# Statik dosyalar ve şablonlar
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Veritabanı ve agent başlatma
db = Database()
agent = Agent()

# WebSocket bağlantıları
active_connections: Dict[str, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında veritabanını başlat"""
    # Veri dizinini oluştur
    if not os.path.exists('data'):
        os.makedirs('data')
    await db.initialize()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket bağlantı noktası"""
    try:
        await websocket.accept()
        active_connections[client_id] = websocket
        
        # Kullanıcı profilini güncelle
        await db.update_user_profile(
            client_id,
            interaction={"last_connection": "websocket"}
        )
        
        while True:
            try:
                # Mesajı al
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Mesaj türüne göre işle
                if message_data.get("type") == "text":
                    # Metin mesajı
                    user_message = message_data["content"]
                    response = await agent.get_response(user_message)
                    
                    # Konuşmayı kaydet
                    await db.save_conversation(
                        client_id,
                        user_message,
                        response["text"],
                        audio_path=response.get("audio"),
                        video_path=response.get("video")
                    )
                    
                    # Yanıtı gönder
                    await websocket.send_json({
                        "type": "response",
                        "text": response["text"],
                        "audio": response.get("audio"),
                        "video": response.get("video")
                    })
                
                elif message_data.get("type") == "audio":
                    # Ses mesajı
                    audio_data = message_data["content"]
                    response = await agent.process_audio(audio_data)
                    
                    # Konuşmayı kaydet
                    await db.save_conversation(
                        client_id,
                        response["transcription"],
                        response["text"],
                        audio_path=response.get("audio"),
                        video_path=response.get("video")
                    )
                    
                    # Yanıtı gönder
                    await websocket.send_json({
                        "type": "response",
                        "text": response["text"],
                        "audio": response.get("audio"),
                        "video": response.get("video"),
                        "transcription": response["transcription"]
                    })
                
                elif message_data.get("type") == "video":
                    # Video mesajı
                    video_data = message_data["content"]
                    response = await agent.process_video(video_data)
                    
                    # Konuşmayı kaydet
                    await db.save_conversation(
                        client_id,
                        response["transcription"],
                        response["text"],
                        audio_path=response.get("audio"),
                        video_path=response.get("video")
                    )
                    
                    # Yanıtı gönder
                    await websocket.send_json({
                        "type": "response",
                        "text": response["text"],
                        "audio": response.get("audio"),
                        "video": response.get("video"),
                        "transcription": response["transcription"]
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": "İşlem sırasında bir hata oluştu."
                })
    
    finally:
        # Bağlantıyı kapat
        if client_id in active_connections:
            del active_connections[client_id]
        try:
            await websocket.close()
        except:
            pass

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Ana sayfa"""
    return templates.TemplateResponse(
        "index.html",
        {"request": None}
    )

@app.get("/history/{client_id}")
async def get_history(client_id: str):
    """Konuşma geçmişini getir"""
    history = await db.get_conversation_history(client_id)
    return {"history": history}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
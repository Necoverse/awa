from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from models import Database
from agent import Agent
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any
import asyncio
from pathlib import Path

# Dizin yolları
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="Teddy AI",
    version="1.0.0",
    description="Teddy AI Web Arayüzü"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı ve agent başlatma
db = Database()
agent = Agent()

# WebSocket bağlantıları
active_connections: Dict[str, WebSocket] = {}

# Dizinleri oluştur
for directory in [STATIC_DIR, TEMPLATES_DIR, STATIC_DIR / "frames", BASE_DIR / "data"]:
    directory.mkdir(exist_ok=True)
    logger.info(f"Dizin oluşturuldu/kontrol edildi: {directory}")

# Statik dosyalar ve templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında veritabanını ve agent'ı başlat"""
    try:
        await db.initialize()
        logger.info("Uygulama başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"Başlatma hatası: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    try:
        if not TEMPLATES_DIR.exists():
            raise FileNotFoundError("Templates dizini bulunamadı")
            
        template_file = TEMPLATES_DIR / "index.html"
        if not template_file.exists():
            raise FileNotFoundError("index.html şablonu bulunamadı")
            
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Ana sayfa yüklenirken hata: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Sayfa yüklenemedi: {str(e)}"}
        )

async def process_message(websocket: WebSocket, client_id: str, message_data: Dict[str, Any]) -> None:
    """Gelen mesajı işle ve yanıt gönder"""
    try:
        message_type = message_data.get("type")
        content = message_data.get("content")

        if not content:
            raise ValueError("Mesaj içeriği boş")

        # Mesaj türüne göre işle
        if message_type == "text":
            response = await agent.get_response(content)
        elif message_type == "audio":
            response = await agent.process_audio(content)
        elif message_type == "video":
            response = await agent.process_video(content)
        else:
            raise ValueError(f"Geçersiz mesaj türü: {message_type}")

        # Konuşmayı kaydet
        if response.get("type") != "error":
            await db.save_conversation(
                client_id,
                content if message_type == "text" else response.get("transcription", ""),
                response["text"],
                audio_path=response.get("audio"),
                video_path=response.get("video")
            )

        # Yanıtı gönder
        await websocket.send_json(response)

    except Exception as e:
        logger.error(f"Mesaj işleme hatası: {str(e)}")
        error_response = {
            "type": "error",
            "text": "İşlem sırasında bir hata oluştu.",
            "details": str(e)
        }
        await websocket.send_json(error_response)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket bağlantı noktası"""
    try:
        await websocket.accept()
        active_connections[client_id] = websocket
        
        # Kullanıcı profilini güncelle
        await db.update_user_profile(
            client_id,
            interaction={"last_connection": datetime.now().isoformat()}
        )
        
        logger.info(f"Yeni WebSocket bağlantısı: {client_id}")
        
        while True:
            try:
                # Mesajı al ve işle
                data = await websocket.receive_text()
                message_data = json.loads(data)
                await process_message(websocket, client_id, message_data)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket bağlantısı kapandı: {client_id}")
                break
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON ayrıştırma hatası: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "text": "Geçersiz mesaj formatı"
                })
                
            except Exception as e:
                logger.error(f"WebSocket hatası: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "text": "Beklenmeyen bir hata oluştu"
                })
    
    finally:
        # Bağlantıyı temizle
        if client_id in active_connections:
            del active_connections[client_id]
        try:
            await websocket.close()
        except:
            pass

@app.get("/history/{client_id}")
async def get_history(client_id: str):
    """Konuşma geçmişini getir"""
    try:
        history = await db.get_conversation_history(client_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Geçmiş alınırken hata: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Geçmiş alınamadı: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(active_connections),
        "agent_status": "active",
        "templates_dir": str(TEMPLATES_DIR),
        "static_dir": str(STATIC_DIR)
    } 
import edge_tts
import asyncio
import tempfile
import base64
import json
import logging
import os
from typing import Dict, Optional, Any
import speech_recognition as sr
import cv2
import numpy as np
from datetime import datetime

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        """Agent sınıfını başlat"""
        self.voice = "tr-TR-AhmetNeural"
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.stop_listening_event = asyncio.Event()
        
        # Ses tanıma ayarları
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.4

    async def text_to_speech(self, text: str) -> Optional[str]:
        """Metni sese çevir ve base64 formatında döndür"""
        try:
            if not text:
                return None

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(temp_file.name)
                
                with open(temp_file.name, "rb") as audio_file:
                    audio_data = base64.b64encode(audio_file.read()).decode()
                
                os.unlink(temp_file.name)
                return audio_data
        except Exception as e:
            logger.error(f"Ses dönüşümü hatası: {str(e)}")
            return None

    async def get_response(self, text: str) -> Dict[str, Any]:
        """Kullanıcı mesajına yanıt oluştur"""
        try:
            # Yanıt metnini oluştur (selamlama olmadan)
            response_text = text.strip()
            
            # Metni sese çevir
            audio_data = await self.text_to_speech(response_text)
            
            return {
                "text": response_text,
                "audio": audio_data,
                "type": "response"
            }
        except Exception as e:
            logger.error(f"Yanıt oluşturma hatası: {str(e)}")
            return {
                "text": "Üzgünüm, bir hata oluştu.",
                "audio": None,
                "type": "error"
            }

    async def process_audio(self, audio_data: str) -> Dict[str, Any]:
        """Ses verisini işle ve yanıt döndür"""
        try:
            if not audio_data:
                raise ValueError("Ses verisi boş")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio_bytes = base64.b64decode(audio_data)
                temp_file.write(audio_bytes)
                temp_file.flush()
                
                with sr.AudioFile(temp_file.name) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language="tr-TR")
                
                os.unlink(temp_file.name)
                
                if not text:
                    raise ValueError("Ses metne çevrilemedi")

                response = await self.get_response(text)
                response["transcription"] = text
                
                return response
        except Exception as e:
            logger.error(f"Ses işleme hatası: {str(e)}")
            return {
                "text": "Ses işlenirken bir hata oluştu.",
                "audio": None,
                "transcription": None,
                "type": "error"
            }

    async def process_video(self, video_data: str) -> Dict[str, Any]:
        """Video verisini işle ve yanıt döndür"""
        try:
            if not video_data:
                raise ValueError("Video verisi boş")

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                video_bytes = base64.b64decode(video_data)
                temp_file.write(video_bytes)
                temp_file.flush()
                
                cap = cv2.VideoCapture(temp_file.name)
                if not cap.isOpened():
                    raise ValueError("Video açılamadı")

                frames = []
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frames.append(frame)
                cap.release()
                
                os.unlink(temp_file.name)
                
                if not frames:
                    raise ValueError("Video karesi bulunamadı")

                # Son kareyi kaydet
                last_frame = frames[-1]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                frame_path = f"frames/frame_{timestamp}.jpg"
                
                os.makedirs("static/frames", exist_ok=True)
                cv2.imwrite(f"static/{frame_path}", last_frame)
                
                response_text = f"Video işlendi ({len(frames)} kare)"
                audio_data = await self.text_to_speech(response_text)
                
                return {
                    "text": response_text,
                    "audio": audio_data,
                    "video": frame_path,
                    "type": "response"
                }
        except Exception as e:
            logger.error(f"Video işleme hatası: {str(e)}")
            return {
                "text": "Video işlenirken bir hata oluştu.",
                "audio": None,
                "video": None,
                "type": "error"
            }

    async def start_listening(self) -> bool:
        """Ses dinlemeyi başlat"""
        try:
            if not self.is_listening:
                self.is_listening = True
                self.stop_listening_event.clear()
                return True
            return False
        except Exception as e:
            logger.error(f"Ses dinleme başlatma hatası: {str(e)}")
            return False

    async def stop_listening(self) -> bool:
        """Ses dinlemeyi durdur"""
        try:
            if self.is_listening:
                self.is_listening = False
                self.stop_listening_event.set()
                return True
            return False
        except Exception as e:
            logger.error(f"Ses dinleme durdurma hatası: {str(e)}")
            return False 
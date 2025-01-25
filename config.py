import os
from typing import Dict, Any
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # API Anahtarları
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Uygulama Ayarları
    MAX_MESSAGE_LENGTH: int = 4000
    MAX_RETRIES: int = 3
    
    # Veritabanı Ayarları
    DATABASE_URL: str = "sqlite:///data/messages.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///data/messages.db"
    
    # JWT Ayarları
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Loglama Ayarları
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "app.log"
    
    @classmethod
    def validate(cls) -> None:
        """Gerekli konfigürasyon değerlerini kontrol et"""
        required_vars = [
            "GOOGLE_API_KEY",
            "JWT_SECRET_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Eksik konfigürasyon değerleri: {', '.join(missing_vars)}")
            
    @classmethod
    def get_database_url(cls) -> str:
        """Veritabanı URL'sini döndür"""
        return cls.DATABASE_URL 
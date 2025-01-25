from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageRequest(BaseModel):
    """Mesaj istek modeli"""
    content: str = Field(
        ...,
        description="Mesaj içeriği",
        example="Merhaba, nasılsın?",
        min_length=1,
        max_length=4000
    )
    platform: str = Field(
        default="web",
        description="Mesaj platformu",
        example="web"
    )

class MessageResponse(BaseModel):
    """Mesaj yanıt modeli"""
    id: int = Field(..., description="Mesaj ID", gt=0)
    content: str = Field(..., description="Mesaj içeriği")
    response: str = Field(..., description="AI yanıtı")
    created_at: datetime = Field(..., description="Oluşturulma zamanı")
    platform: str = Field(..., description="Mesaj platformu")

    class Config:
        from_attributes = True

class TokenRequest(BaseModel):
    """Token istek modeli"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=50)

class TokenResponse(BaseModel):
    """Token yanıt modeli"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="bearer", description="Token tipi")

class ErrorResponse(BaseModel):
    """Hata yanıt modeli"""
    detail: str = Field(..., description="Hata detayı")

class HealthResponse(BaseModel):
    """Sağlık kontrolü yanıt modeli"""
    status: str = Field(
        ...,
        description="Sistem durumu",
        example="healthy"
    )
    timestamp: datetime = Field(
        ...,
        description="Kontrol zamanı"
    ) 
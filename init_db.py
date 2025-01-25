import asyncio
from models import init_models

async def init():
    print("Veritabanı tabloları oluşturuluyor...")
    await init_models()
    print("Veritabanı tabloları başarıyla oluşturuldu!")

if __name__ == "__main__":
    asyncio.run(init()) 
import asyncio
import pytest
from agent import AIAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_voice_interaction():
    """Teddy'nin ses etkileşimini test eder"""
    try:
        # Teddy'yi başlat
        teddy = AIAgent()
        await teddy.initialize()
        
        # Ses etkileşimini başlat
        logger.info("Ses etkileşimi testi başlıyor...")
        await teddy.start_voice_interaction()
        
    except KeyboardInterrupt:
        logger.info("Test kullanıcı tarafından sonlandırıldı")
    except Exception as e:
        logger.error(f"Test sırasında hata: {str(e)}")
        raise

if __name__ == "__main__":
    # Test dosyasını doğrudan çalıştır
    asyncio.run(test_voice_interaction()) 
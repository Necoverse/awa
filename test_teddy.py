import asyncio
from agent import AIAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_teddy():
    try:
        # Teddy'yi oluştur
        teddy = AIAgent()
        
        # Kendini tanıtsın
        print("\n=== Teddy'nin Tanıtımı ===")
        intro = await teddy.introduce_self()
        print(intro)
        
        # Yaratıcı çözüm üretsin
        print("\n=== Teddy'nin Yaratıcı Çözümü ===")
        problem = "Yapay zeka sistemlerinin etik kullanımı için nasıl bir çerçeve önerirsin?"
        solution = await teddy.generate_creative_solution(problem)
        print(solution)
        
        # Evrimleşsin ve yeni nesil oluşsun
        print("\n=== Teddy'nin Evrimi ===")
        evolved_teddy = await teddy.evolve()
        evolved_intro = await evolved_teddy.introduce_self()
        print(f"Evrimleşmiş Teddy (Nesil {evolved_teddy.generation}):")
        print(evolved_intro)
        
        # Durumu kaydet
        print("\n=== Teddy'nin Durumu Kaydediliyor ===")
        await teddy.save_state("teddy_state.json")
        print("Teddy'nin durumu kaydedildi: teddy_state.json")
        
    except Exception as e:
        logger.error(f"Test sırasında hata: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_teddy()) 
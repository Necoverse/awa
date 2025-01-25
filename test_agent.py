import asyncio
import logging
from agent import AIAgent

# Test logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Agent'ı oluştur
        agent = AIAgent()
        logger.info("Agent oluşturuldu")

        # Initialize
        await agent.initialize()
        logger.info("Agent başlatıldı")

        # Kendini tanıt
        intro = await agent.introduce_self()
        print("\nTanıtım:")
        print(intro)

        # Test mesajı gönder
        test_message = "Python'da bir web scraping örneği verebilir misin?"
        print("\nTest mesajı gönderiliyor...")
        response = await agent.get_response(test_message)
        print(f"\nYanıt:\n{response}")

        # Kod analizi testi
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        print("\nKod analizi yapılıyor...")
        analysis = await agent.analyze_code(test_code)
        print(f"\nAnaliz:\n{analysis}")

        # Test üretimi testi
        print("\nTest senaryoları üretiliyor...")
        tests = await agent.generate_tests(test_code)
        print(f"\nTestler:\n{tests}")

        # Yaratıcı çözüm testi
        problem = "Bir e-ticaret sitesinde ürün stok takibi nasıl yapılabilir?"
        print("\nYaratıcı çözüm üretiliyor...")
        solution = await agent.generate_creative_solution(problem)
        print(f"\nÇözüm:\n{solution}")

    except Exception as e:
        logger.error(f"Test sırasında hata: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
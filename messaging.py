import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from twilio.rest import Client
from agent import AIAgent

# .env dosyasından API anahtarlarını yükle
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# AI Ajanını başlat
ai_agent = AIAgent()

class MessagingBot:
    def __init__(self):
        # Telegram uygulamasını başlat
        self.telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Twilio istemcisini başlat
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Telegram komut işleyicilerini ekle
        self.telegram_app.add_handler(CommandHandler("start", self.telegram_start))
        self.telegram_app.add_handler(CommandHandler("help", self.telegram_help))
        self.telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.telegram_message))

    def send_whatsapp_message(self, message):
        """WhatsApp üzerinden mesaj gönder"""
        try:
            # WhatsApp mesajını gönder
            self.twilio_client.messages.create(
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                body=message,
                to=f"whatsapp:{YOUR_PHONE_NUMBER}"
            )
            return True
        except Exception as e:
            print(f"WhatsApp mesajı gönderilemedi: {str(e)}")
            return False

    async def telegram_start(self, update, context):
        """Telegram botunu başlatma komutu"""
        welcome_message = """🤖 AI Kod Asistanı'na hoş geldiniz!

Kullanılabilir komutlar:
!analiz <kod> - Kod analizi yapar
!test <kod> - Test senaryoları oluşturur
!yaz <açıklama> - Yeni kod yazar
!kopya - Ajanın kendisini kopyalar

/help - Bu yardım mesajını gösterir"""
        
        await update.message.reply_text(welcome_message)

    async def telegram_help(self, update, context):
        """Yardım komutu"""
        help_message = """🔍 Kullanılabilir komutlar:

!analiz <kod> - Kod analizi yapar
!test <kod> - Test senaryoları oluşturur
!yaz <açıklama> - Yeni kod yazar
!kopya - Ajanın kendisini kopyalar

Örnek kullanım:
!yaz "Bir sayının asal olup olmadığını kontrol eden fonksiyon yaz"

Not: Kod bloklarını ``` işaretleri arasına alarak gönderebilirsiniz."""
        
        await update.message.reply_text(help_message)

    async def telegram_message(self, update, context):
        """Gelen mesajları işle"""
        try:
            user_message = update.message.text
            response = ai_agent.get_response(user_message)
            
            # Uzun yanıtları böl (Telegram mesaj limiti: 4096 karakter)
            if len(response) > 4000:
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
                    # WhatsApp'a da gönder
                    self.send_whatsapp_message(chunk)
            else:
                await update.message.reply_text(response)
                # WhatsApp'a da gönder
                self.send_whatsapp_message(response)
                
        except Exception as e:
            error_message = f"Hata oluştu: {str(e)}"
            await update.message.reply_text(error_message)
            self.send_whatsapp_message(error_message)

    def start(self):
        """Bot servislerini başlat"""
        print("🤖 Mesajlaşma servisleri başlatılıyor...")
        
        try:
            # Telegram ve WhatsApp servislerini başlat
            print("📱 Telegram ve WhatsApp servisleri başlatılıyor...")
            self.telegram_app.run_polling(allowed_updates=Application.ALL_TYPES)
            
        except Exception as e:
            print(f"❌ Hata oluştu: {str(e)}")

def main():
    # Mesajlaşma botunu başlat
    bot = MessagingBot()
    bot.start()

if __name__ == "__main__":
    main() 
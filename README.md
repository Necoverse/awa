# Yerel AI Ajanı

Bu proje, Google Gemini API'sini kullanarak yerel olarak çalışan basit bir AI ajanı uygulamasıdır.

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun ve Google API anahtarınızı ekleyin:
```
GOOGLE_API_KEY=your_api_key_here
```

## Kullanım

Ajanı başlatmak için:
```bash
python agent.py
```

- Programdan çıkmak için "çıkış", "exit" veya "quit" yazabilirsiniz.
- Her mesajınıza AI yanıt verecektir.

## Özellikler

- Google Gemini Pro modeli kullanır
- Renkli konsol arayüzü
- Basit ve kullanıcı dostu arayüz

## API Anahtarı Alma

1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Oturum açın ve API anahtarı oluşturun
3. Oluşturduğunuz API anahtarını `.env` dosyasına ekleyin 
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config

def setup_logger(name):
    """Uygulama için logger oluştur"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Dosya handler'ı oluştur
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler(
        os.path.join('logs', Config.LOG_FILE),
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    
    # Konsol handler'ı oluştur
    console_handler = logging.StreamHandler()
    
    # Formatter oluştur
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler'lara formatter'ı ekle
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Logger'a handler'ları ekle
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 
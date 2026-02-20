"""
Конфигурация Flask-приложения.
Загружает настройки из переменных окружения (через python-dotenv).
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла, если он существует
load_dotenv()

class Config:
    """Базовый класс конфигурации."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///travelplanner.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Ключ API Яндекс.Карт (обязательно задать в .env)
    YANDEX_MAPS_API_KEY = os.environ.get('YANDEX_MAPS_API_KEY', '')

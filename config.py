"""
Конфигурация Flask-приложения.
Загружает настройки из переменных окружения (через python-dotenv).
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI', 'sqlite:///travelplanner.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    YANDEX_MAPS_API_KEY = os.environ.get(
        'YANDEX_MAPS_API_KEY', '')

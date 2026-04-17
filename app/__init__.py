"""
Пакет веб-приложения TravelPlanner.

Этот пакет содержит веб-приложение для планирования путешествий
с интеграцией Яндекс.Карт.
"""

from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """
    Фабрика приложения Flask.

    Создает и настраивает экземпляр приложения Flask.

    Аргументы:
        config_class: Класс конфигурации (по умолчанию Config)

    Возвращает:
        Flask: Настроенный экземпляр приложения Flask
    """
    # Создание экземпляра приложения Flask
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)

    # Регистрация маршрутов ПОСЛЕ создания приложения
    from app.routes import register_routes
    register_routes(app)

    # Создание таблиц базы данных (если их нет)
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    """
    Загрузка пользователя по ID для Flask-Login.

    Аргументы:
        user_id (str): Идентификатор пользователя

    Возвращает:
        User или None: Экземпляр пользователя, если найден, иначе None
    """
    from app.models import User
    return User.query.get(int(user_id))

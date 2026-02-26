"""
Инициализация Flask-приложения.
"""
from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """Фабрика приложения."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)

    # ВАЖНО: импортируем и регистрируем маршруты ПОСЛЕ создания app
    from app.routes import register_routes
    register_routes(app)

    # Создание таблиц базы данных
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
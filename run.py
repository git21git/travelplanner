"""
Главный файл запуска приложения TravelPlanner.
Создаёт и конфигурирует Flask-приложение, инициализирует базу данных.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Инициализация расширений (без привязки к конкретному приложению)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'          # маршрут для перенаправления неавторизованных
login_manager.login_message = 'Пожалуйста, войдите, чтобы увидеть эту страницу.'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Фабрика приложения."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)

    # Импортируем модели и маршруты внутри фабрики, чтобы избежать циклических импортов
    with app.app_context():
        from models import User  # noqa
        from routes import *     # noqa

        # Создание таблиц базы данных (если их нет)
        db.create_all()

    return app


# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

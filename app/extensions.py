"""
Расширения Flask, вынесенные отдельно для избежания циклических импортов.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы увидеть эту страницу'
login_manager.login_message_category = 'info'
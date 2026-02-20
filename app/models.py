"""
Модели данных для приложения TravelPlanner.
Используется SQLAlchemy ORM.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Модель пользователя.
    
    Атрибуты:
        id (int): Уникальный идентификатор.
        username (str): Имя пользователя.
        email (str): Электронная почта (уникальная).
        password_hash (str): Хэш пароля (сохраняется в зашифрованном виде).
        trips (relationship): Список поездок, принадлежащих пользователю.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Связь с поездками (один ко многим)
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class Trip(db.Model):
    """Модель поездки.
    
    Атрибуты:
        id (int): Уникальный идентификатор.
        title (str): Название поездки.
        start_date (date): Дата начала.
        end_date (date): Дата окончания.
        description (str): Краткое описание (опционально).
        user_id (int): Идентификатор владельца (внешний ключ).
        places (relationship): Список мест в поездке.
    """
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Связь с местами (один ко многим)
    places = db.relationship('Place', backref='trip', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Trip {self.title}>'


class Place(db.Model):
    """Модель места в поездке.
    
    Атрибуты:
        id (int): Уникальный идентификатор.
        name (str): Название места.
        address (str): Адрес (введённый пользователем).
        lat (float): Широта (получена через геокодер).
        lng (float): Долгота.
        notes (str): Заметки (опционально).
        trip_id (int): Идентификатор поездки (внешний ключ).
    """
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)

    def __repr__(self):
        return f'<Place {self.name} in trip {self.trip_id}>'

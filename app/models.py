"""
Модели данных для приложения TravelPlanner.

Этот модуль определяет модели базы данных с использованием SQLAlchemy ORM.
"""

from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(db.Model, UserMixin):
    """
    Модель пользователя приложения.

    Атрибуты:
        id (int): Первичный ключ
        username (str): Отображаемое имя пользователя
        email (str): Уникальный email для входа
        password_hash (str): Хешированный пароль
        created_at (datetime): Временная метка создания аккаунта
        trips (list): Связь с поездками пользователя
    """
    __tablename__ = 'users'  # Имя таблицы в базе данных

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь "один ко многим" с поездками
    trips = db.relationship(
        'Trip',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan')

    def __repr__(self):
        """Строковое представление экземпляра User."""
        return f'<User {self.email}>'


class Trip(db.Model):
    """
    Модель поездки пользователя.

    Атрибуты:
        id (int): Первичный ключ
        title (str): Название поездки
        start_date (date): Дата начала поездки
        end_date (date): Дата окончания поездки
        description (str): Описание поездки (необязательно)
        created_at (datetime): Временная метка создания
        user_id (int): Внешний ключ к таблице User
        places (list): Связь с местами в этой поездке
    """
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False)

    # Связь "один ко многим" с местами
    places = db.relationship(
        'Place',
        backref='trip',
        lazy=True,
        cascade='all, delete-orphan')

    def __repr__(self):
        """Строковое представление экземпляра Trip."""
        return f'<Trip {self.title}>'


class Place(db.Model):
    """
    Модель места в поездке.

    Атрибуты:
        id (int): Первичный ключ
        name (str): Название места
        address (str): Физический адрес
        lat (float): Широта координаты
        lng (float): Долгота координаты
        notes (str): Заметки о месте (необязательно)
        created_at (datetime): Временная метка создания
        trip_id (int): Внешний ключ к таблице Trip
    """
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trip_id = db.Column(
        db.Integer,
        db.ForeignKey('trips.id'),
        nullable=False)

    def __repr__(self):
        """Строковое представление экземпляра Place."""
        return f'<Place {self.name}>'

    def to_dict(self):
        """
        Преобразует объект Place в словарь для JSON-сериализации.

        Используется для передачи данных о местах в JavaScript.

        Возвращает:
            dict: Словарь с атрибутами места
        """
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'notes': self.notes
        }

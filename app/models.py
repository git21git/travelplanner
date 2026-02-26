"""
Модели данных для приложения TravelPlanner.
"""
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    """Модель пользователя."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trips = db.relationship('Trip', backref='user', 
                            lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class Trip(db.Model):
    """Модель поездки."""
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    places = db.relationship('Place', backref='trip', 
                             lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Trip {self.title}>'


class Place(db.Model):
    """Модель места в поездке."""
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)

    def __repr__(self):
        return f'<Place {self.name}>'
    
    def to_dict(self):
        """Преобразует объект места в словарь для JavaScript."""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'notes': self.notes
        }
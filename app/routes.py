"""
Маршруты (контроллеры) веб-приложения TravelPlanner.
"""

from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from app import app, db  # предполагается, что app создаётся в __init__.py
from models import User, Trip, Place
from forms import RegistrationForm, LoginForm, TripForm, PlaceForm
from datetime import datetime

# ---------- Геокодирование (API Яндекс.Карт) ----------
def geocode_address(address):
    """
    Преобразует адрес в координаты (широта, долгота) с помощью Яндекс.Геокодера.
    
    Аргументы:
        address (str): Адрес для геокодирования.
    
    Возвращает:
        tuple (lat, lng) или (None, None) в случае ошибки.
    """
    api_key = current_app.config['YANDEX_MAPS_API_KEY']
    if not api_key:
        flash('Ключ API Яндекс.Карт не настроен. Обратитесь к администратору.', 'danger')
        return None, None

    url = 'https://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': api_key,
        'geocode': address,
        'format': 'json',
        'results': 1
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Извлекаем координаты из ответа
        feature_member = data['response']['GeoObjectCollection']['featureMember']
        if not feature_member:
            flash(f'Адрес "{address}" не найден.', 'warning')
            return None, None
        pos = feature_member[0]['GeoObject']['Point']['pos']
        lng, lat = map(float, pos.split())
        return lat, lng
    except (requests.RequestException, KeyError, ValueError) as e:
        flash(f'Ошибка геокодирования: {str(e)}', 'danger')
        return None, None


# ---------- Маршруты аутентификации ----------
@app.route('/')
def index():
    """Главная страница. Если пользователь авторизован, перенаправляет на список поездок."""
    if current_user.is_authenticated:
        return redirect(url_for('trips'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('trips'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Хэшируем пароль
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрированы! Теперь можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему."""
    if current_user.is_authenticated:
        return redirect(url_for('trips'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Вход выполнен успешно.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('trips'))
        else:
            flash('Неверный email или пароль.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


# ---------- Управление поездками ----------
@app.route('/trips')
@login_required
def trips():
    """Список всех поездок текущего пользователя."""
    user_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    return render_template('trips.html', trips=user_trips)


@app.route('/trips/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    """Создание новой поездки."""
    form = TripForm()
    if form.validate_on_submit():
        trip = Trip(
            title=form.title.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(trip)
        db.session.commit()
        flash('Поездка успешно создана!', 'success')
        return redirect(url_for('trip_detail', trip_id=trip.id))
    return render_template('trip_form.html', form=form, title='Новая поездка')


@app.route('/trips/<int:trip_id>')
@login_required
def trip_detail(trip_id):
    """Детальная страница поездки (список мест и карта)."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)  # Запрет доступа к чужим поездкам
    # Передаём данные для карты: координаты всех мест
    places = trip.places
    return render_template('trip_detail.html', trip=trip, places=places)


@app.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    """Редактирование поездки."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    form = TripForm(obj=trip)  # предзаполняем форму данными из объекта
    if form.validate_on_submit():
        trip.title = form.title.data
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        trip.description = form.description.data
        db.session.commit()
        flash('Поездка обновлена.', 'success')
        return redirect(url_for('trip_detail', trip_id=trip.id))
    return render_template('trip_form.html', form=form, title='Редактирование поездки')


@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    """Удаление поездки."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    db.session.delete(trip)
    db.session.commit()
    flash('Поездка удалена.', 'info')
    return redirect(url_for('trips'))


# ---------- Управление местами ----------
@app.route('/trips/<int:trip_id>/places/new', methods=['GET', 'POST'])
@login_required
def new_place(trip_id):
    """Добавление нового места в поездку."""
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    form = PlaceForm()
    if form.validate_on_submit():
        # Геокодируем адрес
        lat, lng = geocode_address(form.address.data)
        if lat is None or lng is None:
            # Ошибка уже показана через flash, остаёмся на форме
            return render_template('place_form.html', form=form, trip=trip)

        place = Place(
            name=form.name.data,
            address=form.address.data,
            lat=lat,
            lng=lng,
            notes=form.notes.data,
            trip_id=trip.id
        )
        db.session.add(place)
        db.session.commit()
        flash('Место добавлено!', 'success')
        return redirect(url_for('trip_detail', trip_id=trip.id))
    return render_template('place_form.html', form=form, trip=trip)


@app.route('/places/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_place(place_id):
    """Редактирование места."""
    place = Place.query.get_or_404(place_id)
    if place.trip.user_id != current_user.id:
        abort(403)
    form = PlaceForm(obj=place)
    if form.validate_on_submit():
        # Если адрес изменился, перегеокодируем
        if form.address.data != place.address:
            lat, lng = geocode_address(form.address.data)
            if lat is None or lng is None:
                return render_template('place_form.html', form=form, trip=place.trip)
            place.lat = lat
            place.lng = lng
        place.name = form.name.data
        place.address = form.address.data
        place.notes = form.notes.data
        db.session.commit()
        flash('Место обновлено.', 'success')
        return redirect(url_for('trip_detail', trip_id=place.trip_id))
    return render_template('place_form.html', form=form, trip=place.trip)


@app.route('/places/<int:place_id>/delete', methods=['POST'])
@login_required
def delete_place(place_id):
    """Удаление места."""
    place = Place.query.get_or_404(place_id)
    if place.trip.user_id != current_user.id:
        abort(403)
    trip_id = place.trip_id
    db.session.delete(place)
    db.session.commit()
    flash('Место удалено.', 'info')
    return redirect(url_for('trip_detail', trip_id=trip_id))

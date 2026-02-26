"""
Маршруты (контроллеры) веб-приложения TravelPlanner.
"""
from flask import render_template, redirect, url_for
from flask import flash, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User, Trip, Place
from app.forms import RegistrationForm, LoginForm, TripForm, PlaceForm


def register_routes(app):
    """Регистрирует все маршруты в приложении."""
    
    # ---------- Главная страница ----------
    @app.route('/')
    def index():
        """Главная страница."""
        if current_user.is_authenticated:
            return redirect(url_for('trips'))
        return render_template('index.html')
    
    # ---------- Маршруты аутентификации ----------
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Регистрация нового пользователя."""
        if current_user.is_authenticated:
            return redirect(url_for('trips'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_pw = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_pw
            )
            db.session.add(user)
            db.session.commit()
            flash('Вы успешно зарегистрированы!', 'success')
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
            if user and check_password_hash(user.password_hash, 
                                            form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash('Вход выполнен успешно!', 'success')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('trips'))
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
        user_trips = Trip.query.filter_by(user_id=current_user.id)\
            .order_by(Trip.start_date.desc()).all()
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
        
        return render_template('trip_form.html', form=form, title='newпоездка')
    
    @app.route('/trips/<int:trip_id>')
    @login_required
    def trip_detail(trip_id):
        """Детальная страница поездки."""
        trip = Trip.query.get_or_404(trip_id)
        if trip.user_id != current_user.id:
            abort(403)

        return render_template('trip_detail.html', trip=trip)

    @app.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_trip(trip_id):
        """Редактирование поездки."""
        trip = Trip.query.get_or_404(trip_id)
        if trip.user_id != current_user.id:
            abort(403)

        form = TripForm(obj=trip)
        if form.validate_on_submit():
            trip.title = form.title.data
            trip.start_date = form.start_date.data
            trip.end_date = form.end_date.data
            trip.description = form.description.data
            db.session.commit()
            flash('Поездка обновлена.', 'success')
            return redirect(url_for('trip_detail', trip_id=trip.id))

        return render_template('trip_form.html', form=form, title='Editпоездк')

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
            # Временно используем тестовые координаты
            lat, lng = 55.751574, 37.573856  # Москва

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

    # ---------- API для карты ----------
    @app.route('/api/trips/<int:trip_id>/places')
    @login_required
    def get_trip_places(trip_id):
        """API endpoint для получения мест поездки в формате JSON."""
        trip = Trip.query.get_or_404(trip_id)
        if trip.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403

        places = []
        for place in trip.places:
            places.append({
                'id': place.id,
                'name': place.name,
                'address': place.address,
                'lat': place.lat,
                'lng': place.lng,
                'notes': place.notes
            })
        return jsonify(places)
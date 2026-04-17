"""
Маршруты (контроллеры) веб-приложения TravelPlanner.

Этот модуль содержит все URL-маршруты и обработчики HTTP-запросов.
Каждый маршрут соответствует определенному действию в приложении:
- Аутентификация пользователей (регистрация, вход, выход)
- Управление поездками (CRUD операции)
- Управление местами (добавление, редактирование, удаление)
- API для взаимодействия с картой

Все маршруты, требующие авторизации, защищены декоратором @login_required.
"""

from flask import render_template, redirect, url_for
from flask import flash, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User, Trip, Place
from app.forms import RegistrationForm, LoginForm, TripForm, PlaceForm


def register_routes(app):
    """
    Регистрирует все маршруты в приложении Flask.

    Эта функция является основным регистратором маршрутов. Она принимает
    экземпляр приложения Flask и добавляет к нему все обработчики URL.

    Аргументы:
        app: Экземпляр приложения Flask, к которому регистрируются маршруты

    Примечание:
        Функция должна вызываться ПОСЛЕ создания приложения, но ДО его запуска.
    """

    @app.route('/')
    def index():
        """
        Главная страница приложения.

        Поведение:
            - Неавторизованный пользователь: показывает главную страницу
            - Авторизованный пользователь: редирект на /trips

        Возвращает:
            str: HTML-шаблон главной страницы (index.html)
            или HTTP-редирект на страницу со списком поездок
        """
        if current_user.is_authenticated:
            return redirect(url_for('trips'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        Регистрация нового пользователя.

        Обрабатывает как отображение формы регистрации (GET-запрос),
        так и отправку данных формы (POST-запрос).

        Процесс регистрации:
            1. Пользователь заполняет форму (имя, email, пароль)
            2. Система валидирует данные
            3. Пароль хешируется для безопасности
            4. Создается запись в базе данных
            5. Пользователь перенаправляется на страницу входа

        Безопасность:
            - Пароль никогда не хранится в открытом виде
            - Используется werkzeug.security для хеширования
            - Проверяется уникальность email

        Возвращает:
            GET: HTML-шаблон формы регистрации (register.html)
            POST (успех): редирект на страницу входа
            POST (ошибка): форма регистрации с сообщениями об ошибках
        """
        # Если пользователь уже вошел в систему, регистрация не
        # нужна
        if current_user.is_authenticated:
            return redirect(url_for('trips'))

        # Создаем экземпляр формы регистрации
        form = RegistrationForm()

        # Проверяем, была ли отправлена форма и прошла ли
        # валидацию
        if form.validate_on_submit():
            # Хешируем пароль перед сохранением в БД
            hashed_password = generate_password_hash(
                form.password.data)

            # Создаем нового пользователя
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password
            )

            # Сохраняем в базу данных
            db.session.add(user)
            db.session.commit()

            # Уведомляем пользователя об успешной регистрации
            flash(
                'Вы успешно зарегистрированы! Теперь можете войти в систему.',
                'success')

            # Перенаправляем на страницу входа
            return redirect(url_for('login'))

        # При GET-запросе или ошибках валидации показываем форму
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Вход зарегистрированного пользователя в систему.

        Аутентифицирует пользователя по email и паролю,
        создает пользовательскую сессию.

        Процесс входа:
            1. Пользователь вводит email и пароль
            2. Система ищет пользователя с таким email
            3. Проверяется соответствие пароля (через хеш)
            4. Создается сессия через Flask-Login
            5. Пользователь перенаправляется на запрошенную страницу или список поездок

        Безопасность:
            - Пароль сравнивается только с хешем
            - Поддерживается параметр 'next' для безопасного редиректа
            - Сессия управляется Flask-Login

        Возвращает:
            GET: HTML-шаблон формы входа (login.html)
            POST (успех): редирект на запрошенную страницу или /trips
            POST (ошибка): форма входа с сообщением об ошибке
        """
        # Перенаправляем уже авторизованных пользователей
        if current_user.is_authenticated:
            return redirect(url_for('trips'))

        form = LoginForm()

        if form.validate_on_submit():
            # Ищем пользователя по email (email уникален)
            user = User.query.filter_by(
                email=form.email.data).first()

            # Проверяем: существует ли пользователь и правильный
            # ли пароль
            if user and check_password_hash(
                    user.password_hash, form.password.data):
                # Вход в систему - создаем сессию
                login_user(user)

                # Получаем URL для перенаправления (если есть)
                # 'next' параметр используется для редиректа на исходную страницу
                next_page = request.args.get('next')

                flash(
                    'Добро пожаловать! Вы успешно вошли в систему.',
                    'success')

                # Перенаправляем на запрошенную страницу или на
                # список поездок
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('trips'))
            else:
                # Ошибка аутентификации
                flash(
                    'Неверный email или пароль. Пожалуйста, попробуйте снова.',
                    'danger')

        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        """
        Выход пользователя из системы.

        Завершает текущую пользовательскую сессию и перенаправляет
        на главную страницу.

        Требования:
            Пользователь должен быть авторизован (@login_required)

        Возвращает:
            HTTP-редирект на главную страницу с сообщением о выходе
        """
        logout_user()
        flash('Вы вышли из системы. До новых встреч!', 'info')
        return redirect(url_for('index'))

    @app.route('/trips')
    @login_required
    def trips():
        """
        Отображает список всех поездок текущего пользователя.

        Поездки сортируются по дате начала (от новых к старым).
        Каждая поездка отображается в виде карточки с краткой информацией:
        - Название
        - Даты поездки
        - Количество мест
        - Кнопки действий (просмотр, редактирование, удаление)

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            str: HTML-шаблон со списком поездок (trips.html)
        """
        # Запрашиваем из БД все поездки текущего пользователя
        user_trips = Trip.query.filter_by(
            user_id=current_user.id) .order_by(
            Trip.start_date.desc()).all()

        return render_template('trips.html', trips=user_trips)

    @app.route('/trips/new', methods=['GET', 'POST'])
    @login_required
    def new_trip():
        """
        Создание новой поездки.

        GET: Отображает пустую форму для создания поездки.
        POST: Обрабатывает данные формы и сохраняет новую поездку.

        Процесс создания:
            1. Пользователь заполняет форму (название, даты, описание)
            2. Система валидирует данные (даты не противоречат друг другу)
            3. Создается объект Trip, связанный с текущим пользователем
            4. Объект сохраняется в базу данных
            5. Пользователь перенаправляется на страницу созданной поездки

        Валидация:
            - Название обязательно (не более 200 символов)
            - Даты начала и окончания обязательны
            - Дата окончания не может быть раньше даты начала
            - Описание опционально (не более 500 символов)

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            GET: HTML-шаблон формы создания поездки (trip_form.html)
            POST (успех): редирект на страницу деталей поездки
            POST (ошибка): форма с сообщениями об ошибках
        """
        form = TripForm()

        if form.validate_on_submit():
            # Создаем новую поездку, связываем с текущим
            # пользователем
            trip = Trip(
                title=form.title.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                description=form.description.data,
                user_id=current_user.id  # Привязываем поездку к пользователю
            )

            # Сохраняем в базу данных
            db.session.add(trip)
            db.session.commit()

            flash(f'Поездка "{trip.title}" успешно создана!', 'success')

            # Перенаправляем на страницу с деталями новой поездки
            return redirect(
                url_for(
                    'trip_detail',
                    trip_id=trip.id))

        # При GET-запросе показываем пустую форму
        return render_template(
            'trip_form.html',
            form=form,
            title='Новая поездка')

    @app.route('/trips/<int:trip_id>')
    @login_required
    def trip_detail(trip_id):
        """
        Детальная страница конкретной поездки.

        Отображает полную информацию о поездке:
        - Название, даты, описание
        - Интерактивную карту со всеми местами
        - Список мест с возможностью редактирования и удаления
        - Кнопки управления поездкой

        Аргументы:
            trip_id (int): Уникальный идентификатор поездки (из URL)

        Безопасность:
            Проверяется, что поездка принадлежит текущему пользователю.
            Если нет - возвращается ошибка 403 (Forbidden).

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            str: HTML-шаблон с деталями поездки (trip_detail.html)
            Или ошибку 404, если поездка не найдена
            Или ошибку 403, если нет прав доступа
        """
        # Ищем поездку в БД или возвращаем 404
        trip = Trip.query.get_or_404(trip_id)

        # Проверка прав доступа
        if trip.user_id != current_user.id:
            abort(403)  # Запрещено - чужая поездка

        # Преобразуем места в список словарей для передачи в
        # JavaScript
        places_data = [place.to_dict() for place in trip.places]

        return render_template('trip_detail.html',
                               trip=trip,
                               places_data=places_data)

    @app.route('/trips/<int:trip_id>/edit',
               methods=['GET', 'POST'])
    @login_required
    def edit_trip(trip_id):
        """
        Редактирование существующей поездки.

        GET: Отображает форму с предзаполненными данными поездки.
        POST: Обрабатывает обновленные данные и сохраняет их в БД.

        Аргументы:
            trip_id (int): Идентификатор редактируемой поездки

        Процесс редактирования:
            1. Загружается существующая поездка из БД
            2. Форма предзаполняется текущими значениями
            3. Пользователь изменяет нужные поля
            4. Система валидирует новые данные
            5. Обновления сохраняются в базу данных

        Безопасность:
            Проверяется владение поездкой перед редактированием

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            GET: HTML-шаблон формы редактирования (trip_form.html)
            POST (успех): редирект на страницу деталей поездки
            POST (ошибка): форма с сообщениями об ошибках
        """
        # Загружаем поездку из БД
        trip = Trip.query.get_or_404(trip_id)

        # Проверка прав доступа
        if trip.user_id != current_user.id:
            abort(403)

        # Создаем форму, предзаполненную данными из объекта trip
        form = TripForm(obj=trip)

        if form.validate_on_submit():
            # Обновляем поля поездки новыми значениями из формы
            trip.title = form.title.data
            trip.start_date = form.start_date.data
            trip.end_date = form.end_date.data
            trip.description = form.description.data

            # Сохраняем изменения в БД
            db.session.commit()

            flash('Поездка успешно обновлена!', 'success')
            return redirect(
                url_for(
                    'trip_detail',
                    trip_id=trip.id))

        return render_template(
            'trip_form.html',
            form=form,
            title='Редактирование поездки')

    @app.route('/trips/<int:trip_id>/delete', methods=['POST'])
    @login_required
    def delete_trip(trip_id):
        """
        Удаление поездки.

        Удаляет поездку и ВСЕ связанные с ней места (каскадное удаление).

        Аргументы:
            trip_id (int): Идентификатор удаляемой поездки

        Каскадное удаление:
            Благодаря настройке cascade='all, delete-orphan' в модели Trip,
            все места, принадлежащие поездке, будут удалены автоматически.

        Безопасность:
            Проверяется владение поездкой перед удалением

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            HTTP-редирект на страницу со списком поездок
        """
        trip = Trip.query.get_or_404(trip_id)

        if trip.user_id != current_user.id:
            abort(403)

        # Сохраняем название для сообщения (до удаления объекта)
        trip_title = trip.title

        # Удаляем поездку (каскадно удалятся и все места)
        db.session.delete(trip)
        db.session.commit()

        flash(
            f'Поездка "{trip_title}" и все её места удалены.',
            'info')
        return redirect(url_for('trips'))

    @app.route('/trips/<int:trip_id>/places/new',
               methods=['GET', 'POST'])
    @login_required
    def new_place(trip_id):
        """
        Добавление нового места в поездку.

        GET: Отображает форму для добавления места.
        POST: Обрабатывает данные места и определяет координаты через API.

        Аргументы:
            trip_id (int): ID поездки, в которую добавляется место

        Процесс добавления места:
            1. Пользователь вводит название и адрес места
            2. Система отправляет запрос к Яндекс.Геокодеру
            3. Полученные координаты (широта, долгота) сохраняются
            4. Если геокодирование не удалось - используются координаты по умолчанию
            5. Место сохраняется в БД и отображается на карте

        Геокодирование:
            Используется API Яндекс.Карт для преобразования адреса в координаты.
            URL: https://geocode-maps.yandex.ru/1.x/

        Обработка ошибок:
            - Если адрес не найден - используются координаты Москвы
            - Если API недоступен - показывается предупреждение
            - Координаты по умолчанию: 55.751574, 37.573856 (Москва, Кремль)

        Требования:
            Пользователь должен быть авторизован
            Поездка должна принадлежать пользователю

        Возвращает:
            GET: HTML-шаблон формы добавления места (place_form.html)
            POST (успех): редирект на страницу деталей поездки
            POST (ошибка): форма с сообщениями об ошибках
        """
        # Загружаем поездку и проверяем права доступа
        trip = Trip.query.get_or_404(trip_id)

        if trip.user_id != current_user.id:
            abort(403)

        form = PlaceForm()

        if form.validate_on_submit():
            # Инициализируем координаты значением None
            lat, lng = None, None

            try:
                import requests
                from flask import current_app

                # Получаем API ключ из конфигурации приложения
                api_key = current_app.config['YANDEX_MAPS_API_KEY']

                # Формируем адрес для запроса (кодируем для URL)
                address = form.address.data

                # Запрос к Яндекс.Геокодеру API
                # Документация:
                # https://yandex.ru/dev/maps/geocoder/
                url = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={address}&format=json"

                # Отправляем GET-запрос к API
                response = requests.get(url)
                data = response.json()

                # Парсим ответ API
                # Структура ответа: response ->
                # GeoObjectCollection -> featureMember ->
                # GeoObject -> Point -> pos
                try:
                    # Координаты приходят в формате "долгота
                    # широта"
                    pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                    # Разделяем и преобразуем в числа
                    lng, lat = map(float, pos.split())
                except (KeyError, IndexError, ValueError) as e:
                    # Если не удалось получить координаты,
                    # используем значения по умолчанию
                    lat, lng = 55.751574, 37.573856
                    flash(
                        'Не удалось определить координаты по указанному адресу. '
                        'Место будет отмечено в центре Москвы.', 'warning')

            except Exception as e:
                # В случае любой ошибки (нет интернета, проблемы
                # с API и т.д.)
                lat, lng = 55.751574, 37.573856
                flash(f'Ошибка при определении координат: { str(e)}. ' 'Место будет отмечено в центре Москвы.', 'warning')

            # Создаем объект места с полученными координатами
            place = Place(
                name=form.name.data,
                address=form.address.data,
                lat=lat,
                lng=lng,
                notes=form.notes.data,
                trip_id=trip.id
            )

            # Сохраняем место в базу данных
            db.session.add(place)
            db.session.commit()

            flash(f'Место "{place.name}" успешно добавлено в поездку!', 'success')
            return redirect(
                url_for(
                    'trip_detail',
                    trip_id=trip.id))

        return render_template(
            'place_form.html', form=form, trip=trip)

    @app.route('/places/<int:place_id>/edit',
               methods=['GET', 'POST'])
    @login_required
    def edit_place(place_id):
        """
        Редактирование существующего места.

        Позволяет изменить название, адрес или заметки места.

        Аргументы:
            place_id (int): Идентификатор редактируемого места

        Безопасность:
            Проверяется, что место принадлежит поездке текущего пользователя

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            GET: HTML-шаблон формы редактирования места (place_form.html)
            POST (успех): редирект на страницу деталей поездки
            POST (ошибка): форма с сообщениями об ошибках
        """
        # Загружаем место из БД
        place = Place.query.get_or_404(place_id)

        # Проверяем, что место принадлежит текущему пользователю
        if place.trip.user_id != current_user.id:
            abort(403)

        # Создаем форму, предзаполненную данными места
        form = PlaceForm(obj=place)

        if form.validate_on_submit():
            # Обновляем только текстовые поля (координаты не
            # меняем)
            place.name = form.name.data
            place.address = form.address.data
            place.notes = form.notes.data

            # Сохраняем изменения
            db.session.commit()

            flash('Место успешно обновлено!', 'success')
            return redirect(
                url_for(
                    'trip_detail',
                    trip_id=place.trip_id))

        return render_template(
            'place_form.html',
            form=form,
            trip=place.trip)

    @app.route('/places/<int:place_id>/delete', methods=['POST'])
    @login_required
    def delete_place(place_id):
        """
        Удаление места из поездки.

        Удаляет только конкретное место, не затрагивая поездку.

        Аргументы:
            place_id (int): Идентификатор удаляемого места

        Безопасность:
            Используется метод POST (не GET) для защиты от CSRF
            Проверяется владение местом через цепочку place.trip.user

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            HTTP-редирект обратно на страницу деталей поездки
        """
        place = Place.query.get_or_404(place_id)

        if place.trip.user_id != current_user.id:
            abort(403)

        # Сохраняем ID поездки для редиректа (до удаления
        # объекта)
        trip_id = place.trip_id
        place_name = place.name

        # Удаляем место
        db.session.delete(place)
        db.session.commit()

        flash(f'Место "{place_name}" удалено из поездки.', 'info')
        return redirect(url_for('trip_detail', trip_id=trip_id))

    @app.route('/api/trips/<int:trip_id>/places')
    @login_required
    def get_trip_places(trip_id):
        """
        API endpoint для получения списка мест поездки в формате JSON.

        Используется для динамической загрузки мест на карту без перезагрузки страницы.
        Возвращает данные в формате, удобном для JavaScript (JSON).

        Аргументы:
            trip_id (int): ID поездки, места которой нужно получить

        Формат ответа:
            [
                {
                    "id": 1,
                    "name": "Красная площадь",
                    "address": "Москва, Красная площадь",
                    "lat": 55.7537,
                    "lng": 37.6199,
                    "notes": "Красивое место"
                },
                ...
            ]

        Безопасность:
            Проверяется, что поездка принадлежит текущему пользователю

        Требования:
            Пользователь должен быть авторизован

        Возвращает:
            JSON: Список мест поездки в формате JSON
            Или JSON с ошибкой 403, если нет доступа
        """
        # Загружаем поездку
        trip = Trip.query.get_or_404(trip_id)

        # Проверка прав доступа
        if trip.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403

        # Формируем JSON-ответ
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

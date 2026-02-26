"""
Определение форм для ввода данных пользователем.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from datetime import date


# Импортируем модель User внутри функции, чтобы избежать циклического импорта
def get_user_model():
    from app.models import User
    return User


class RegistrationForm(FlaskForm):
    """Форма регистрации нового пользователя."""
    username = StringField(
        'Имя пользователя', 
        validators=[DataRequired(message="Обязательное поле"), Length(min=2, max=80, message="Имя должно быть от 2 до 80 символов")],
        render_kw={"class": "form-control", "placeholder": "Введите имя"}
    )
    email = StringField(
        'Электронная почта', 
        validators=[DataRequired(message="Обязательное поле"), Email(message="Введите корректный email")],
        render_kw={"class": "form-control", "placeholder": "example@mail.com"}
    )
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired(message="Обязательное поле"), Length(min=6, message="Пароль должен быть минимум 6 символов")],
        render_kw={"class": "form-control", "placeholder": "Минимум 6 символов"}
    )
    confirm_password = PasswordField(
        'Подтвердите пароль', 
        validators=[DataRequired(message="Обязательное поле"), EqualTo('password', message="Пароли должны совпадать")],
        render_kw={"class": "form-control", "placeholder": "Повторите пароль"}
    )
    submit = SubmitField(
        'Зарегистрироваться',
        render_kw={"class": "btn btn-primary w-100"}
    )

    def validate_email(self, email):
        """Проверка уникальности email."""
        User = get_user_model()
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Пользователь с таким email уже существует.')


class LoginForm(FlaskForm):
    """Форма входа в систему."""
    email = StringField(
        'Электронная почта', 
        validators=[DataRequired(message="Обязательное поле"), Email(message="Введите корректный email")],
        render_kw={"class": "form-control", "placeholder": "example@mail.com"}
    )
    password = PasswordField(
        'Пароль', 
        validators=[DataRequired(message="Обязательное поле")],
        render_kw={"class": "form-control", "placeholder": "Введите пароль"}
    )
    submit = SubmitField(
        'Войти',
        render_kw={"class": "btn btn-primary w-100"}
    )
    
    remember_me = StringField(render_kw={"class": "form-check-input"})


class TripForm(FlaskForm):
    """Форма создания/редактирования поездки."""
    title = StringField(
        'Название поездки', 
        validators=[DataRequired(message="Введите название поездки"), Length(max=200, message="Слишком длинное название")],
        render_kw={"class": "form-control", "placeholder": "Например: Лето в Сочи 2024"}
    )
    start_date = DateField(
        'Дата начала', 
        format='%Y-%m-%d',
        validators=[DataRequired(message="Выберите дату начала")],
        render_kw={"class": "form-control", "type": "date"}
    )
    end_date = DateField(
        'Дата окончания', 
        format='%Y-%m-%d',
        validators=[DataRequired(message="Выберите дату окончания")],
        render_kw={"class": "form-control", "type": "date"}
    )
    description = TextAreaField(
        'Описание', 
        validators=[Optional(), Length(max=500, message="Описание не должно превышать 500 символов")],
        render_kw={"class": "form-control", "placeholder": "Краткое описание поездки...", "rows": 4}
    )
    submit = SubmitField(
        'Сохранить',
        render_kw={"class": "btn btn-primary"}
    )

    def validate_end_date(self, end_date):
        """Проверка, что дата окончания не раньше даты начала."""
        if self.start_date.data and end_date.data and end_date.data < self.start_date.data:
            raise ValidationError('Дата окончания не может быть раньше даты начала.')


class PlaceForm(FlaskForm):
    """Форма добавления места в поездку."""
    name = StringField(
        'Название места', 
        validators=[DataRequired(message="Введите название места"), Length(max=200, message="Слишком длинное название")],
        render_kw={"class": "form-control", "placeholder": "Например: Красная площадь"}
    )
    address = StringField(
        'Адрес', 
        validators=[DataRequired(message="Введите адрес"), Length(max=300, message="Слишком длинный адрес")],
        render_kw={"class": "form-control", "placeholder": "Москва, Красная площадь, 1"}
    )
    notes = TextAreaField(
        'Заметки', 
        validators=[Optional(), Length(max=500, message="Заметки не должны превышать 500 символов")],
        render_kw={"class": "form-control", "placeholder": "Что здесь интересного? Часы работы, контакты...", "rows": 3}
    )
    submit = SubmitField(
        'Добавить место',
        render_kw={"class": "btn btn-success"}
    )
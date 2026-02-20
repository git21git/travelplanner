"""
Определение форм для ввода данных пользователем.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    """Форма регистрации нового пользователя."""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        """Проверка уникальности email."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Пользователь с таким email уже существует.')


class LoginForm(FlaskForm):
    """Форма входа в систему."""
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class TripForm(FlaskForm):
    """Форма создания/редактирования поездки."""
    title = StringField('Название поездки', validators=[DataRequired(), Length(max=200)])
    start_date = DateField('Дата начала', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Дата окончания', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    submit = SubmitField('Сохранить')

    # Кастомная валидация дат: окончание не может быть раньше начала
    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data and end_date.data < self.start_date.data:
            raise ValidationError('Дата окончания не может быть раньше даты начала.')


class PlaceForm(FlaskForm):
    """Форма добавления места в поездку."""
    name = StringField('Название места', validators=[DataRequired(), Length(max=200)])
    address = StringField('Адрес', validators=[DataRequired(), Length(max=300)])
    notes = TextAreaField('Заметки', validators=[Length(max=500)])
    submit = SubmitField('Добавить место')

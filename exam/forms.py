from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, EmailField)
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(),
                                             Length(min=3, max=100)])
    
    password = StringField('Пароль', validators=[InputRequired(),
                                             Length(min=3, max=100)])


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(),
                                             Length(min=3, max=100), ])

    first_name = StringField('Имя', validators=[InputRequired(),
                                             Length(min=3, max=100)])

    last_name = StringField('Фамилия', validators=[InputRequired(),
                                             Length(min=3, max=100)])

    email = EmailField('Email', validators=[InputRequired(),
                                             Length(min=3, max=100)])

    password = StringField('Пароль', validators=[InputRequired(),
                                             Length(min=3, max=100)])

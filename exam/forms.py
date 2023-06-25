from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, EmailField, FileField, SelectMultipleField, SelectField)
from wtforms.validators import InputRequired, Length
import models
from sqlalchemy.orm import load_only


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired(),
                                             Length(min=3, max=100)])
    
    password = StringField('Пароль', validators=[InputRequired(),
                                             Length(min=3, max=100)])
    
    remember_me = BooleanField('Запомнить меня')


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


class NewBookForm(FlaskForm):
    name = StringField('Название', validators=[InputRequired(),
                                             Length(min=3, max=255),])

    short_description = TextAreaField('Краткое описание', validators=[InputRequired(),])

    year = StringField('Год', validators=[InputRequired(),
                                             Length(min=1, max=4),])

    publisher = StringField('Издательство', validators=[InputRequired(),
                                             Length(min=3, max=255),])

    author = StringField('Автор', validators=[InputRequired(),
                                             Length(min=3, max=255),])

    pages = IntegerField('Объем (страниц)', validators=[InputRequired(),])

    cover_id = FileField('Обложка', validators=[InputRequired(),])

    genre = SelectMultipleField('Жанры')

    def __init__(self, mode="new"):
        super(NewBookForm, self).__init__()

        self.genre.choices = [(c.id, c.name) for c in models.Genre.query.all()]

        if mode == 'edit':
            self.cover_id.validators = []

        self.genre.name = "genre[]"


class NewReviewForm(FlaskForm):
    rating = SelectField('Ваша оценка', coerce=int, validators=[InputRequired(),], choices=[
        (5, '5 – отлично',),
        (4, '4 – хорошо',),
        (3, '3 – удовлетворительно',),
        (2, '2 – неудовлетворительно',),
        (1, '1 – плохо',),
        (0, '0 – ужасно'),
    ], default=5)

    text = TextAreaField('Текст рецензии', validators=[InputRequired(),])

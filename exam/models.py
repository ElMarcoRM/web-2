from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import backref


db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)

    description = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(50), unique=True, nullable=False)

    first_name = db.Column(db.String(50), nullable=False)

    last_name = db.Column(db.String(50), nullable=False)

    patronymic = db.Column(db.String(50), nullable=True)

    role_id = db.Column(db.String(50), db.ForeignKey('role.id'), nullable=False)

    email = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(50), nullable=False)

    role = db.relationship("Role", backref=backref("role.id", cascade="all, delete"))

    def __repr__(self):
        return self.login


class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    file = db.Column(db.String(255), nullable=False)

    mime_type = db.Column(db.String(255), nullable=False)

    md5_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.file


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)

    short_description = db.Column(db.Text(), nullable=False)

    year = db.Column(db.String(4), nullable=False)

    publisher = db.Column(db.String(50), nullable=False)

    author = db.Column(db.String(50), nullable=False)

    pages = db.Column(db.String(50), nullable=False)

    cover_id = db.Column(db.Integer, db.ForeignKey('cover.id'))

    cover = db.relationship("Cover", backref="cover")

    reviews = db.relationship("Review", backref="review")

    def __repr__(self):
        return self.name


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class BookGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))

    genre = db.relationship("Genre", backref="genre.id")

    book = db.relationship("Book", backref=backref("book.id", cascade="all,delete"))


class ReviewStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    rating = db.Column(db.Integer)

    text = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user = db.relationship("User", backref=backref("user.id", cascade="all, delete"))

    status_id = db.Column(db.Integer, db.ForeignKey('review_status.id'), nullable=False)

    status = db.relationship("ReviewStatus", backref=backref("review_status.id", cascade="all,delete"))

    book = db.relationship("Book")

    def __repr__(self):
        return self.text

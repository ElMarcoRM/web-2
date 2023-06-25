from flask import Flask, jsonify, render_template, redirect, url_for, request, flash, abort, send_from_directory, session
import data_accessor
import flask_login
import forms
import models
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.sql import func
import seed_db
import secrets, os
from PIL import Image
import hashlib, bleach
from flask_paginate import Pagination, get_page_parameter, get_page_args
import markdown


login_manager = flask_login.LoginManager()


app = Flask(__name__, static_url_path='/static/', 
            static_folder='static')
app.secret_key = 'flask-insecure-f+7=#^z18vefavl0o-7p)0e&578t)@r-tr8h0m%9@1ct64kdmd'
migrate = Migrate(app, models.db, render_as_batch=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://std_2164_exam:12345678@std-mysql.ist.mospolytech.ru/std_2164_exam"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://std_2164_exam:Stud801286!@std-mysql/std_2164_exam"
models.db.init_app(app)

login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')

def register_commands(app):
    """Register CLI commands."""
    app.cli.add_command(seed_db.seed)

register_commands(app)


@login_manager.user_loader
def load_user(user):
    return models.User.query.get(user)


@app.route('/')
def index():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', default=1)
    books_all = models.db.session.query(models.Book).order_by(models.Book.year.desc()).all()
    books = models.db.session.query(models.Book).order_by(models.Book.year.desc()).limit(per_page).offset(offset).all()

    book_reviews, book_reviews_count = [], []
    for book in books:
        book_reviews.append(models.db.session.query(func.avg(models.Review.rating).label('avg')).filter_by(book_id=book.id).first())
        book_reviews_count.append(models.db.session.query(func.count(models.Review.id).label('count')).filter_by(book_id=book.id).first())

    pagination = Pagination(page=page, per_page=per_page, total=len(books_all),
                            record_name="books", show_single_page=True)

    return render_template('index.html', books=zip(books, book_reviews, book_reviews_count), pagination=pagination)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = models.User.query.filter_by(login=request.form.get('login')).first()
            remember_me = request.form.get('remember_me')
            if remember_me == "on":
                remember_me = True
            else:
                remember_me = False

            if not user or not check_password_hash(user.password, request.form.get('password')):
                session.pop('_flashes', None)
                flash('Невозможно аутентифицироваться с указанными логином и паролем')
                return redirect('/login')
            else:
                flask_login.login_user(user, remember=remember_me)

                return redirect('/')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if request.method == "POST":
        if form.validate():
            user = models.User(
                login=form.login.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                role_id=models.Role.query.filter_by(name="пользователь").first().id,
                password=generate_password_hash(form.password.data),
            )

            try:
                models.db.session.add(user)
                models.db.session.commit()
                session.pop('_flashes', None)
                flash('Для продолжения войдите в аккаунт')
            except Exception as e:
                print(e)
                models.db.session.rollback()
                return render_template('register.html', form=form)

            return redirect('/login')
        else:
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')


def save_cover_image(form_picture, picture_path):
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


@app.route('/books/new', methods=['GET', 'POST'])
@flask_login.login_required
def new_book():
    if flask_login.current_user.role.name != "администратор":
        abort(401)

    form = forms.NewBookForm()

    if request.method == "POST":
        file = request.files.get('cover_id')

        cover_id = 0

        if file:
            mimetype = file.content_type

        if form.validate():
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(app.root_path, 'media/covers', picture_fn)

            cover = models.Cover(
                file=picture_fn,
                mime_type=mimetype,
                md5_hash=file.filename,
            )

            try:
                models.db.session.add(cover)
                models.db.session.flush()

                cover_id = cover.id

                models.db.session.commit()
            except Exception as e:
                session.pop('_flashes', None)
                flash('Произошла ошибка')
                models.db.session.rollback()
                return render_template('book_new.html', form=form)

            save_cover_image(form.cover_id.data, picture_path)

            book = models.Book(
                name=bleach.clean(form.name.data),
                short_description=bleach.clean(form.short_description.data),
                year=form.year.data,
                publisher=form.publisher.data,
                author=form.author.data,
                pages=form.pages.data,
                cover_id=cover_id,
            )

            try:
                models.db.session.add(book)
                models.db.session.commit()
            except Exception as e:
                session.pop('_flashes', None)
                flash('Произошла ошибка')
                models.db.session.rollback()
                return render_template('book_new.html', form=form)

            
            book_genres = []
            for genre in request.form.getlist('genre[]'):
                book_genre = models.BookGenre(
                    book_id=book.id,
                    genre_id=genre
                )
                book_genres.append(book_genre)
            try:
                models.db.session.add_all(book_genres)
                models.db.session.commit()
            except Exception as e:
                session.pop('_flashes', None)
                flash('Произошла ошибка')
                models.db.session.rollback()
                return render_template('book_new.html', form=form)

            return redirect('/books/%s'%book.id)
        else:
            return render_template('book_new.html', form=form)

    return render_template('book_new.html', form=form)


@app.route('/books/<int:id>', methods=['GET', 'POST'])
def book_index(id):
    book = models.Book.query.get(id)
    book_genres = models.BookGenre.query.filter_by(book_id=id).all()

    reviews = models.Review.query.filter_by(book_id=id, status_id=2)

    reviewed = False

    if flask_login.current_user.is_authenticated:
        if models.Review.query.filter_by(book_id=id, user_id=flask_login.current_user.id).all() != []:
            reviewed = True
    else:
        reviewed = None

    return render_template('book_index.html', book=book, book_genres=book_genres, reviews=reviews, reviewed=reviewed)


@app.route('/reviews/new/<int:book_id>', methods=['GET', 'POST'])
@flask_login.login_required
def new_review(book_id):
    form = forms.NewReviewForm()

    if request.method == "POST":
        if form.validate():
            review = models.Review(
                book_id=book_id,
                user_id=flask_login.current_user.id,
                rating=form.rating.data,
                text=bleach.clean(form.text.data),
                status_id=1,
            )

            try:
                models.db.session.add(review)
                models.db.session.commit()
            except Exception as e:
                session.pop('_flashes', None)
                flash('Произошла ошибка')
                models.db.session.rollback()
                return render_template('review_new.html', form=form)

            return redirect('/books/%s'%book_id)
        else:
            return render_template('review_new.html', form=form)

    return render_template('review_new.html', form=form)


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


@app.route('/books/delete/<int:id>')
def delete_book(id):
    if flask_login.current_user.role.name != 'администратор':
        abort(401)

    book = models.db.session.query(models.Book).get(id)
    book_name = book.name

    reviews = models.db.session.query(models.Review).filter_by(book_id=id)

    for review in reviews:
        models.db.session.delete(review)

    models.db.session.delete(book)
    models.db.session.commit()

    session.pop('_flashes', None)

    flash("Книга %s успешно удалена"%book_name)

    return render_template('book_delete.html')


@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    if flask_login.current_user.role.name != 'администратор':
        abort(401)

    form = forms.NewBookForm(mode="edit")
    book = models.db.session.query(models.Book).get(id)

    if request.method == "POST":
        if form.validate():
            book = models.Book.query.get(id)
            book.name = bleach.clean(form.name.data)
            book.short_description = bleach.clean(form.short_description.data)
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data

            try:
                models.db.session.commit()
            except Exception as e:
                session.pop('_flashes', None)
                flash('Произошла ошибка')
                models.db.session.rollback()
                return render_template('book_new.html', form=form)

            return redirect('/books/%s'%book.id)
        else:
            return render_template('book_edit.html', book=book, form=form)

    return render_template('book_edit.html', book=book, form=form)


@app.route('/reviews/<int:user_id>', methods=['GET', 'POST'])
def reviews_list(user_id):
    reviews = models.db.session.query(models.Review).filter_by(user_id=user_id).all()

    for review in reviews:
        review.text = markdown.markdown(review.text)

    return render_template('reviews_list.html', reviews=reviews)


@app.route('/reviews/all', methods=['GET'])
def reviews_all():
    if flask_login.current_user.role.name != 'модератор':
        abort(401)

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', default=1)
    reviews_all = models.db.session.query(models.Review).order_by(models.Review.created_at.desc()).all()
    reviews = models.db.session.query(models.Review).order_by(models.Review.created_at.desc()).limit(per_page).offset(offset).all()

    for review in reviews:
        review.text = markdown.markdown(review.text)

    pagination = Pagination(page=page, per_page=per_page, total=len(reviews_all),
                            record_name="reviews", show_single_page=True)

    return render_template('reviews_all.html', reviews=reviews, pagination=pagination)


@app.route('/review/make_decision/<int:id>', methods=['GET'])
def review_index(id):
    if flask_login.current_user.role.name != 'модератор':
        abort(401)

    review = models.Review.query.get(id)

    return render_template('reviews_index.html', review=review)


@app.route('/review/make_decision/accept/<int:id>', methods=['GET'])
def review_accept(id):
    if flask_login.current_user.role.name != 'модератор':
        abort(401)

    review = models.Review.query.get(id)
    review.status_id = 2

    models.db.session.commit()

    return redirect('/reviews/all')


@app.route('/review/make_decision/deny/<int:id>', methods=['GET'])
def review_deny(id):
    if flask_login.current_user.role.name != 'модератор':
        abort(401)

    review = models.Review.query.get(id)
    review.status_id = 3

    models.db.session.commit()

    return redirect('/reviews/all')

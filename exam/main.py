from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
import data_accessor
import flask_login
import forms
import models
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import PendingRollbackError


login_manager = flask_login.LoginManager()


app = Flask(__name__)
app.secret_key = 'flask-insecure-f+7=#^z18vefavl0o-7p)0e&578t)@r-tr8h0m%9@1ct64kdmd'
migrate = Migrate(app, models.db)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
models.db.init_app(app)

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user):
    print("USERRRRRRRRRR: ", user)
    return models.User.query.get(user)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            print("DSADDASA: s", request.form.get('login'))
            user = models.User.query.filter_by(login=request.form.get('login')).first()

            if not user or not check_password_hash(user.password, request.form.get('password')):
                flash('Неправильный логин или пароль')
                return redirect('/login')
            else:
                flask_login.login_user(user)

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
                password=generate_password_hash(form.password.data),
            )

            try:
                models.db.session.add(user)
                models.db.session.commit()
                flash('Для продолжения войдите в аккаунт')
            except Exception as e:
                flash('Пользователь с таким логином уже существует')
                models.db.session.rollback()
                return render_template('register.html', form=form)

            return redirect('/login')
        else:
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('index.html')

# @flask_login.login_required

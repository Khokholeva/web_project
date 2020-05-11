import os
import datetime
from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from data import db_session, __all_models
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

User = __all_models.user.User
Question = __all_models.question.Question
Test = __all_models.test.Test

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_project_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    profile_pic = FileField('Аватарка')
    submit = SubmitField('Войти')


class AccountForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    profile_pic = FileField('Аватарка')
    submit = SubmitField('Изменить аккаунт')


class PasswordForm(FlaskForm):
    password_old = PasswordField('Введите старый пароль', validators=[DataRequired()])
    password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить пароль')


def main():
    path = os.getcwd().replace('\\', '/') + '/db'
    if not os.path.exists(path):
        os.mkdir(path)

    db_session.global_init("db/tests.sqlite")
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    session = db_session.create_session()

    if current_user.is_authenticated:
        if current_user.completed_tests:
            completed = list(map(int, current_user.completed_tests.split('')))
        else:
            completed = []
        tests = session.query(Test).filter(Test.user != current_user, Test.id not in completed)
        print(tests[0].id not in completed)
    else:
        tests = session.query(Test).filter().all()

    return render_template('main.html', title='Just Tests', data=tests)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if form.profile_pic.data:
            profile_pic_name = form.profile_pic.data.filename
            path = os.getcwd().replace('\\', '/') + '/static/img'
            if not os.path.exists(path):
                os.mkdir(path)
            save_name = form.name.data + '_' + profile_pic_name
            profile_pic_name = 'static/img/' + save_name
            form.profile_pic.data.save(profile_pic_name)
        else:
            profile_pic_name = ''
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            profile_pic=profile_pic_name
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        logout_user()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = AccountForm()
    session = db_session.create_session()
    user = current_user
    user = session.query(User).filter(User.email == user.email).first()
    profile_pic_name = user.profile_pic
    if request.method == "GET":
        form.name.data = user.name
        form.about.data = user.about
    if form.validate_on_submit():
        if form.profile_pic.data:
            profile_pic_name = form.profile_pic.data.filename
            save_name = form.name.data + '_' + profile_pic_name
            profile_pic_name = 'static/img/' + save_name
            form.profile_pic.data.save(profile_pic_name)
            user.profile_pic = profile_pic_name
        user.name = form.name.data
        user.about = form.about.data
        user.created_date = datetime.datetime.now()
        session.commit()
        return render_template('my_account.html', title='Мой аккаунт', form=form, email=user.email,
                               path=profile_pic_name, message='Аккаунт изменён')
    return render_template('my_account.html', title='Мой аккаунт', form=form, email=user.email,
                           path=profile_pic_name)


@app.route('/pass_change', methods=['GET', 'POST'])
@login_required
def pass_change():
    form = PasswordForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = current_user
        user = session.query(User).filter(User.email == user.email).first()
        if not user.check_password(form.password_old.data):
            return render_template('pass.html', title='Изменение пароля',
                                   message="Введён неправильный пароль", form=form)
        if form.password.data != form.password_again.data:
            return render_template('pass.html', title='Изменение пароля',
                                   message="Пароли не совпадают", form=form)
        user.set_password(form.password.data)
        session.commit()
        return render_template('pass.html', title='Изменение пароля',
                               message="Пароль изменён", form=form)
    return render_template('pass.html', title='Изменение пароля', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user_delete')
@login_required
def user_delete():
    session = db_session.create_session()
    user = current_user
    user = session.query(User).filter(User.email == user.email).first()
    session.delete(user)
    session.commit()
    return redirect("/")


@app.route('/test_info/<id>')
@login_required
def test_page(id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == id).first()
    return render_template('test_page.html', test=test, title='О тесте')


@app.route('/complete_test/<id>', methods=['POST', 'GET'])
@login_required
def complete_test(id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == id).first()
    ques_ids = list(map(int, test.questions.split('')))
    all_questions = [session.query(Question).filter(Question.id == qu_id).first() for qu_id in ques_ids]
    if request.method == 'GET':
        return render_template('complete_test.html', questions=all_questions, title='Прохождение теста')
    elif request.method == 'POST':
        user = session.query(User).filter(User.email == current_user.email).first()
        user.completed_tests = user.completed_tests + '' + str(id)
        result = 0
        for key in request.form.keys():
            ind = key.split('_')[-1]
            corr = session.query(Question).filter(Question.id == ind).first().correct
            if request.form[key] == corr:
                result += 1
        max_res = len(ques_ids)
        experience = test.difficulty * 10 * result
        if result == max_res:
            experience *= 1.2
        user.xp += experience
        session.commit()
        return render_template('result.html', result=result, max_res=max_res, experience=experience)


if __name__ == '__main__':
    main()

import os
import datetime
from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from data import db_session, __all_models
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.fields.html5 import EmailField, SearchField
from wtforms.validators import DataRequired

User = __all_models.user.User
Question = __all_models.question.Question
Test = __all_models.test.Test
Category = __all_models.category.Category

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_project_key'
login_manager = LoginManager()
login_manager.init_app(app)


# Форма для входа в систему зарегистрировавшегося ранее пользователя
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')  ##


# Форма для регистрации нового пользователя
class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    profile_pic = FileField('Аватарка')
    submit = SubmitField('Войти')


# Форма для просмотра информации об аккаунте
class AccountForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    profile_pic = FileField('Аватарка')
    submit = SubmitField('Изменить аккаунт')


# Форма для изменения пароля пользователя
class PasswordForm(FlaskForm):
    password_old = PasswordField('Введите старый пароль', validators=[DataRequired()])
    password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить пароль')


# Форма для создания/редактирования теста
class TestForm(FlaskForm):
    name = StringField('Название')
    about = TextAreaField('Описание теста')
    category = SearchField('Категория (по умолчанию без категории)')
    difficulty = SelectField('Сложность от 0 до 5 (по умолчанию 0)',
                             choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)])
    attachment = FileField('Прикрепить файл')
    submit = SubmitField('Сохранить')


# Инициализация бд, запуск приложения
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


# Главная страница, содержит список тестов
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    completed = []
    difficulies = ['any', 0, 1, 2, 3, 4, 5]
    categories = ['any'] + [el.name for el in session.query(Category)]
    authors = ['any', 'Без автора'] + [el.name for el in session.query(User) if el != current_user]
    official = ['any', "Только официальные", 'Только не официальные']
    moder_difficulty = [1, 2, 3, 4, 5]
    if request.method == 'POST':
        if current_user.is_authenticated:
            if request.form.get('moderator'):
                if current_user.moderator:
                    tests = session.query(Test).filter().all()
                    id, diff = request.form['moderator'].split('_')
                    test = session.query(Test).filter(Test.id == int(id)).first()
                    test.difficulty = int(diff)
                    test.official = True
                    session.commit()
            else:
                if current_user.completed_tests:
                    completed = list(map(int, current_user.completed_tests.split('')))

                if request.form['difficulty'] == 'any':
                    tests = session.query(Test).filter(Test.user != current_user, Test.id not in completed)
                else:
                    tests = session.query(Test).filter(Test.user != current_user,
                                                       Test.id not in completed,
                                                       Test.difficulty == request.form['difficulty'])

                if request.form['category'] != 'any':
                    tests = [test for test in tests if test.category == request.form['category']]

                if request.form['author'] == 'Без автора':
                    tests = [test for test in tests if not test.user]
                elif request.form['author'] != 'any':
                    tests = [test for test in tests if test.user]
                    tests = [test for test in tests if test.user.name == request.form['author']]

                if request.form['official'] == 'Только официальные':
                    tests = [test for test in tests if test.official]
                elif request.form['official'] == 'Только не официальные':
                    tests = [test for test in tests if not test.official]

        else:
            tests = session.query(Test).filter().all()
    else:
        if current_user.is_authenticated:
            if current_user.completed_tests:
                completed = list(map(int, current_user.completed_tests.split('')))

            tests = session.query(Test).filter(Test.user != current_user, Test.id not in completed)
        else:
            tests = session.query(Test).filter().all()

    return render_template('main.html', title='Just Tests', data=tests, completed=completed,
                           option=difficulies, option_2=categories, option_3=authors, option_4=official,
                           option_mod=moder_difficulty)



# Вход в систему
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


# Регистрация в системе
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


# Информация о своем аккаунте, возможность изменить данные, создать новый тест
@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = AccountForm()
    session = db_session.create_session()
    user = current_user
    user = session.query(User).filter(User.email == user.email).first()
    profile_pic_name = user.profile_pic[7:]
    data = [session.query(Test).filter(Test.id == int(id)).first() for id in user.user_tests.split('')]
    if 0 in data:
        data.remove(0)
    if None in data:
        data.remove(None)
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
            profile_pic_name = profile_pic_name[7:]
        user.name = form.name.data
        user.about = form.about.data
        user.created_date = datetime.datetime.now()
        session.commit()
        return render_template('my_account.html', title='Мой аккаунт', form=form, email=user.email,
                               path=profile_pic_name, message='Аккаунт изменён', xp=user.xp, data=data)
    return render_template('my_account.html', title='Мой аккаунт', form=form, email=user.email,
                           path=profile_pic_name, xp=user.xp, data=data)


# Изменение пароля
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


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Удаление аккаунта
@app.route('/user_delete/<id>')
@login_required
def user_delete(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    if user:
        session.delete(user)
        session.commit()
        return redirect("/")
    else:
        return "User not found"


# Основная информация о тесте, ссылка для прохождения теста
@app.route('/test_info/<id>')
@login_required
def test_page(id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == int(id)).first()
    completed = list(map(int, current_user.completed_tests.split('')))
    return render_template('test_page.html', test=test, title='О тесте', completed=completed)


# Прохождение теста / результат теста
@app.route('/complete_test/<id>', methods=['POST', 'GET'])
@login_required
def complete_test(id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == int(id)).first()
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
        return render_template('result.html', result=result, max_res=max_res, experience=experience,
                               title='Результат')


# Просмотр информации о другом пользователе, доступ к его тестам
@app.route('/other_account/<id>', methods=['GET', 'POST'])
@login_required
def other_account(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == int(id)).first()
    if user:
        data = session.query(Test).filter(Test.user == user)
        if request.method == 'POST':
            if current_user.moderator:
                change_id, diff = request.form['moderator'].split('_')
                test = session.query(Test).filter(Test.id == int(change_id)).first()
                test.difficulty = int(diff)
                test.official = True
                session.commit()
        dont_show = list(map(int, current_user.completed_tests.split('')))
        return render_template('other_account.html', user=user, completed=dont_show, title='Аккаунт ' + user.name,
                               data=data, option_mod=[1, 2, 3, 4, 5])
    else:
        return 'User not found'


# Создание нового теста/редактирование старого
@app.route('/edit_test/<id>', methods=['GET', 'POST'])
@login_required
def edit_test(id):
    session = db_session.create_session()
    form = TestForm()
    categories = [el.name for el in session.query(Category)]
    form.category.choices = categories
    if int(id) == 0:
        if not current_user.moderator:
            form.difficulty.choices = [('0', 0)]
            form.difficulty.label = 'Выбор сложности недоступен'
        pic_name = 'img/'
        if form.validate_on_submit():
            test = Test()
            user = current_user
            user = session.query(User).filter(User.email == user.email).first()
            if form.attachment.data:
                pic_name = 'static/img/' + form.name.data + '_' + form.attachment.data.filename
                form.attachment.data.save(pic_name)
                test.attachment = pic_name
                pic_name = pic_name[7:]
            test.name = form.name.data
            test.about = form.about.data
            test.category = form.category.data
            test.difficulty = int(form.difficulty.data)
            test.user = user
            if current_user.moderator:
                test.official = True
            if form.category.data not in [el.name for el in session.query(Category)]:
                cat = Category()
                cat.name = form.category.data
                session.add(cat)
            session.add(test)
            session.commit()
            user.user_tests += '' + str(test.id)
            session.commit()
            return render_template('edit_test.html', title='Создание теста', form=form,
                                   path=pic_name, message='Изменения сохранены')
        return render_template('edit_test.html', form=form, path=pic_name, title='Создание теста')
    else:
        test = session.query(Test).filter(Test.id == int(id)).first()
        if test:
            if test.user == current_user:
                pic_name = test.attachment[7:] if test.attachment else 'img/'
                if request.method == 'GET':
                    form.name.data = test.name
                    form.category.data = test.category
                    form.about.data = test.about
                    form.difficulty.data = str(test.difficulty)
                if form.validate_on_submit():
                    print('g')
                    if form.attachment.data:
                        pic_name = 'static/img/' + form.name.data + '_' + form.attachment.data.filename
                        form.attachment.data.save(pic_name)
                        test.attachment = pic_name
                        pic_name = pic_name[7:]
                    test.name = form.name.data
                    test.about = form.about.data
                    test.category = form.category.data
                    if current_user.moderator:
                        test.difficulty = int(form.difficulty.data)
                    else:
                        test.official = False
                        test.difficulty = 0
                    if form.category.data not in [el.name for el in session.query(Category)]:
                        cat = Category()
                        cat.name = form.category.data
                        session.add(cat)
                    session.commit()
                    return render_template('edit_test.html', title='Редактирование теста', form=form,
                                           path=pic_name, message='Изменения сохранены')
                return render_template('edit_test.html', title='Редактирование теста', form=form,
                                       path=pic_name)

            else:
                return 'AccessError'
        else:
            return "Test not found"


# Удаление теста
@app.route('/delete_test/<id>')
@login_required
def delete_test(id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == int(id)).first()
    if test:
        if test.user == current_user or current_user.moderator:
            user = session.query(User).filter(User.email == test.user.email).first()
            session.delete(test)
            tests = user.user_tests.split('')
            del tests[tests.index(str(id))]
            user.user_tests = ''.join(tests) if len(tests) > 1 else tests[0]
            session.commit()
            return redirect(request.args['redir'])
        else:
            return 'AccessError'
    else:
        return "Test not found"


if __name__ == '__main__':
    main()

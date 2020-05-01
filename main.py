from flask import Flask, render_template
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_project_key'


def main():
    db_session.global_init("db/tests.sqlite")
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Домашняя страница')


if __name__ == '__main__':
    main()

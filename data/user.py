import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Класс пользователя, содержит информацию о пользователе, список его тестов и тестов, пройденных им,
# функции для создания пароля
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    profile_pic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, default='')
    about = sqlalchemy.Column(sqlalchemy.String, default='')
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    tests = orm.relation("Test", back_populates='user')
    completed_tests = sqlalchemy.Column(sqlalchemy.String, default='0')
    user_tests = sqlalchemy.Column(sqlalchemy.String, default='0')
    moderator = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    xp = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

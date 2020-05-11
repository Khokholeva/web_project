import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# Класс теста, содержит инфорацию о тесте, список id вопросов теста
class Test(SqlAlchemyBase):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, default='Без категории')
    about = sqlalchemy.Column(sqlalchemy.String, default='Без описания')
    attachment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    questions = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    difficulty = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user = orm.relation('User')
    official = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

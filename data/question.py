import sqlalchemy
from .db_session import SqlAlchemyBase


# Класс вопроса, содержит текст, варианты ответов, правильный ответ
class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    attachment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    correct = sqlalchemy.Column(sqlalchemy.String, nullable=True)

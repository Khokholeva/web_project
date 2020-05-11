import sqlalchemy
from .db_session import SqlAlchemyBase


# Класс категории, просто для сохранения списка категорий
class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
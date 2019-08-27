# TASK-6 : SQLAlchemy ORM models added

from flask_sqlalchemy import SQLAlchemy
from alayatodo import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/alayatodo.db'
db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(255), nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=False)
    todo_res = db.relationship('Todos', backref='user')


class Todos(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complete = db.Column(db.Integer, default=0)
    description = db.Column(db.VARCHAR(255))




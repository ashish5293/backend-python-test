# TASK-2 : Database migration script to alter table todos and add a new field named "complete"
# To upgrade to this db version following commands need to be run before running the server
# python resources/migrate.py db init
# python resources/migrate.py db migrate
# python resources/migrate.py db upgrade

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))

from alayatodo import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/alayatodo.db'
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(255), nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=False)
    todo_res = db.relationship('todos', backref='user')


class Todos(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complete = db.Column(db.Integer, default=0)
    description = db.Column(db.VARCHAR(255))


if __name__ == '__main__':
    manager.run()

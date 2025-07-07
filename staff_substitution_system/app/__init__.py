# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey123'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .routes import app as main_app
app.register_blueprint(main_app)

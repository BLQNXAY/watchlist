from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

login_manager = LoginManager(app)

from watchlist.models import User

@login_manager.user_loader
def load_user(user_id):
	user = User.query.get(int(user_id))
	return user

login_manager.login_view = 'login'


@app.context_processor
def inject_user():
	user = User.query.first()
	return dict(user=user)

from watchlist import views, errors, commands
from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))

class Movie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60))
	year = db.Column(db.String(4))


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
def initdb(drop):
	if drop:
		db.drop_all()
	db.create_all()
	click.echo('Initialized database')

@app.cli.command()
def forge():
	db.create_all()

	name = 'Grey Li'
	movies = [
		{'title': 'My Neighbor Totoro', 'year': '1988'},
		{'title': 'Dead Poets Society', 'year': '1989'},
		{'title': 'A Perfect World', 'year': '1993'},
		{'title': 'Leon', 'year': '1994'},
		{'title': 'Mahjong', 'year': '1996'},
		{'title': 'Swallowtail Butterfly', 'year': '1996'},
		{'title': 'King of Comedy', 'year': '1999'},
		{'title': 'Devils on the Doorstep', 'year': '1999'},
		{'title': 'WALL-E', 'year': '2008'},
		{'title': 'The Pork of Music', 'year': '2012'},
	]

	user = User(name=name)
	db.session.add(user)
	for m in movies:
		movie = Movie(title=m['title'], year=m['year'])
		db.session.add(movie)

	db.session.commit()
	click.echo('Done')


@app.route('/')
@app.route('/index')
def index():
	user = db.query.first()
	movies = db.query.all()
	return render_template('index.html', user=user, movies=movies)

@app.route('/user/<name>')
def user_page(name):
	return 'User : %s' % name

@app.route('/test')
def test_url_for():
	print(url_for('user_page', name='XAY'))
	print(url_for('test_url_for', page=2))
	return 'Test page'
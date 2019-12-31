import pytest
import tempfile

from app import app, db, Movie, User, forge, initdb

class TestWatchlist:
	@pytest.fixture()
	def init(self, request):
		app.config.update(
			TESTING = True,
			SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
			)

		db.create_all()
		user = User(name='TestName', username='testusername')
		user.set_password('testpassword')
		movie = Movie(title='Test Movie Title', year='2019')
		db.session.add_all([user, movie])
		db.session.commit()

		def final():
			db.session.remove()
			db.drop_all()

		request.addfinalizer(final)
		

	@pytest.fixture()
	def client(self, init):
		return app.test_client()

	@pytest.fixture
	def runner(self, init):
		return app.test_cli_runner()
	
	def login(self, client):
		data = {
			'username': 'testusername',
			'password': 'testpassword'
		}
		client.post('/login', data=data, follow_redirects=True)

	def logout(self, client):
		client.get('/logout', follow_redirects=True)


	def test_app_exist(self, client):
		assert app != None

	def test_app_is_testing(self, client):
		assert app.config['TESTING'] == True

	def test_404_page(self, client):
		response = client.get('/nothing', follow_redirects=True)
		data = response.data
		assert b'Page Not Found - 404' in data
		assert b'Go Back' in data
		assert response.status_code == 404

	def test_index_page(self, client):
		response = client.get('/', follow_redirects=True)
		data = response.data
		assert b'TestName\'s Watchlist' in data
		assert b'Test Movie Title' in data
		assert response.status_code == 200

	def test_create_item(self, client):
		self.login(client)

		response = client.post('/', data=dict(title='New movie', year='2020'), follow_redirects=True)
		data = response.data
		assert b'Item created' in data
		assert b'New movie' in data

		response = client.post('/', data=dict(title='', year='2020'), follow_redirects=True)
		data = response.data
		assert b'Item created' not in data
		assert b'Invalid input' in data

		response = client.post('/', data=dict(title='New movie', year=''), follow_redirects=True)
		data = response.data
		assert b'Item created' not in data
		assert b'Invalid input' in data
		
	def test_update_item(self, client):
		self.login(client)

		response = client.get('/movie/edit/1', follow_redirects=True)
		data = response.data
		assert b'Edit item' in data
		assert b'Test Movie Title' in data
		assert b'2019' in data

		response = client.post('/movie/edit/1', data=dict(title='New Movie Edited', year='2020'), follow_redirects=True)
		data = response.data
		assert b'Item updated' in data
		assert b'New Movie Edited' in data

		response = client.post('/movie/edit/1', data=dict(title='', year='2020'), follow_redirects=True)
		data = response.data
		assert b'Item updated' not in data
		assert b'Invalid input' in data

		response = client.post('/movie/edit/1', data=dict(title='New Movie Edited', year=''), follow_redirects=True)
		data = response.data
		assert b'Item updated' not in data
		assert b'Invalid input' in data

	def test_delete_item(self, client):
		self.login(client)

		response = client.post('/movie/delete/1', follow_redirects=True)
		data = response.data
		assert b'Item deleted' in data
		assert b'Test Movie Title' not in data

	def test_login_protect(self, client):
		response = client.get('/', follow_redirects=True)
		data = response.data
		assert b'Logout' not in data
		assert b'Edit' not in data
		assert b'Add' not in data
		assert b'Delete' not in data
		assert b'Settings' not in data
		assert b'<form method="post">' not in data

	def test_login(self, client):
		response = client.post('/login', data=dict(username='testusername', password='testpassword'), follow_redirects=True)
		data = response.data
		assert b'Login success' in data
		assert b'Logout' in data
		assert b'Edit' in data
		assert b'Add' in data
		assert b'Delete' in data
		assert b'Settings' in data
		assert b'<form method="post">' in data

		response = client.post('/login', data=dict(username='testusername', password='wrongpassword'), follow_redirects=True)
		data = response.data
		assert b'Login success' not in data
		assert b'Invalid username or password' in data

		response = client.post('/login', data=dict(username='wrongusername', password='wrongpassword'), follow_redirects=True)
		data = response.data
		assert b'Login success' not in data
		assert b'Invalid username or password' in data

		response = client.post('/login', data=dict(username='', password='wrongpassword'), follow_redirects=True)
		data = response.data
		assert b'Login success' not in data
		assert b'Invalid input' in data

		response = client.post('/login', data=dict(username='testusername', password=''), follow_redirects=True)
		data = response.data
		assert b'Login success' not in data
		assert b'Invalid input' in data

	def test_logut(self, client):
		self.login(client)

		response = client.get('/logout', follow_redirects=True)
		data = response.data
		assert b'Goodbye' in data
		assert b'Logout' not in data
		assert b'Edit' not in data
		assert b'Add' not in data
		assert b'Delete' not in data
		assert b'Settings' not in data
		assert b'<form method="post">' not in data

	def test_settings(self, client):
		self.login(client)

		response = client.get('/settings', follow_redirects=True)
		data = response.data
		assert b'Settings' in data
		assert b'Your Name' in data

		response = client.post('/settings', data=dict(name='XAY'), follow_redirects=True)
		data = response.data
		assert b'Settings updated' in data
		assert b'XAY' in data

		response = client.post('/settings', data=dict(name=''), follow_redirects=True)
		data = response.data
		assert b'Settings updated' not in data
		assert b'Invalid input' in data

	def test_forge_command(self, runner):
		result = runner.invoke(forge)
		assert 'Done' in result.output
		assert Movie.query.count() != 0

	def test_initdb_command(self, runner):
		result = runner.invoke(initdb)
		assert 'Initialized database' in result.output

	def test_admin_command(self, runner):
		db.drop_all()
		db.create_all()
		result = runner.invoke(args=['admin', '--username', 'XAY', '--password', '123'])
		assert 'Creating user...' in result.output
		assert 'Done' in result.output
		assert User.query.count() == 1
		assert User.query.first().username == 'XAY'
		assert User.query.first().validate_password('123')


	def test_admin_update_command(self, runner):
		result = runner.invoke(args=['admin', '--username', 'XAI', '--password', '456'])
		assert 'Updating user...' in result.output
		assert 'Done' in result.output
		assert User.query.count() == 1
		assert User.query.first().username == 'XAI'
		assert User.query.first().validate_password('456')

if __name__ == '__main__':
	pytest.main()
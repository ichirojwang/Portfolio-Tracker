import pytest

from flasktracker import create_app, db, bcrypt
from flasktracker.config import TestConfig
from flasktracker.users.models import User


class AuthActions:
    def __init__(self, client, name="LeBron James", email="lebron@gmail.com", password="akronohio"):
        self.client = client
        self.name = name
        self.email = email
        self.password = password

    def create(self):
        with self.client.application.app_context():
            hashed_password = bcrypt.generate_password_hash(self.password).decode('utf-8')
            test_user = User(self.name, self.email, hashed_password)
            test_user_2 = User("John Doe", "johndoe@gmail.com", hashed_password)
            db.session.add(test_user)
            db.session.add(test_user_2)
            db.session.commit()

    def login(self):
        return self.client.post('/login', data={"email": self.email, "password": self.password})

    def logout(self):
        return self.client.get('/logout')


@pytest.fixture()
def app():
    app = create_app(config_class=TestConfig)

    with app.app_context():
        db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth(client):
    return AuthActions(client)

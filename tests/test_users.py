from flasktracker.users.models import User


def test_signup_get(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Sign Up</title>" in response.data


def test_signup_post(app, client):
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                                 "confirm_password": "testpassword"})
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "lebron@gmail.com"
        assert response.status_code == 302
        assert response.headers['Location'] == "/login"


def test_signup_confirm_pass_fail(app, client):
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                                 "confirm_password": "testpasswordd"})
    with app.app_context():
        assert User.query.count() == 0
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Sign Up</title>" in response.data


def test_signup_empty_fields(app, client):
    response = client.post('/signup',
                           data={"name": "", "email": "lebron@gmail.com", "password": "testpassword",
                                 "confirm_password": "testpassword"})
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "", "password": "testpassword",
                                 "confirm_password": "testpassword"})
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "",
                                 "confirm_password": ""})
    with app.app_context():
        assert User.query.count() == 0
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Sign Up</title>" in response.data

def test_profile_get(app, client):

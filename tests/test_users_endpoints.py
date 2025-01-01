from flask_login import current_user

from flasktracker import db
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


def test_signup_long_name(app, client):
    # 40 chars max for name
    response = client.post('/signup',
                           data={"name": "LeBron James verylongnamewith40character", "email": "lebron40char@gmail.com",
                                 "password": "testpassword",
                                 "confirm_password": "testpassword"})
    assert response.status_code == 302
    assert response.headers['Location'] == "/login"
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "lebron40char@gmail.com"

    response = client.post('/signup',
                           data={"name": "LeBron James verylongnamewith41characters", "email": "lebron41char@gmail.com",
                                 "password": "testpassword",
                                 "confirm_password": "testpassword"})
    assert b"<title>Loonie Ledger - Sign Up</title>" in response.data
    with app.app_context():
        assert User.query.count() == 1
        assert response.status_code == 200


def test_signup_short_password(app, client):
    # password min 8 char
    # try with 8 char
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron8char@gmail.com", "password": "12345678",
                                 "confirm_password": "12345678"})
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "lebron8char@gmail.com"
        assert response.status_code == 302
        assert response.headers['Location'] == "/login"
    # try with 7 char
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron7char@gmail.com", "password": "1234567",
                                 "confirm_password": "1234567"})
    assert b"<title>Loonie Ledger - Sign Up</title>" in response.data
    with app.app_context():
        assert User.query.count() == 1
        assert response.status_code == 200


def test_signup_password_no_match(app, client):
    # password and confirm_password no match
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebronnomatch@gmail.com", "password": "testpassword",
                                 "confirm_password": "badpassword"})
    assert b"<title>Loonie Ledger - Sign Up</title>" in response.data
    with app.app_context():
        assert User.query.count() == 0
        assert response.status_code == 200


def test_signup_empty_fields(app, client):
    # checking if empty fields work
    client.post('/signup',
                data={"name": "", "email": "lebron@gmail.com", "password": "testpassword",
                      "confirm_password": "testpassword"})
    client.post('/signup',
                data={"name": "LeBron James", "email": "", "password": "testpassword",
                      "confirm_password": "testpassword"})
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "",
                                 "confirm_password": ""})
    with app.app_context():
        assert User.query.count() == 0
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Sign Up</title>" in response.data


def test_signup_duplicate(app, client):
    # checking if duplicate emails can be used to sign up
    client.post('/signup',
                data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                      "confirm_password": "testpassword"})
    response = client.post('/signup',
                           data={"name": "LeBron James Jr", "email": "lebron@gmail.com", "password": "testpassword",
                                 "confirm_password": "testpassword"})
    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "lebron@gmail.com"
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Sign Up</title>" in response.data
        assert b"That email already exists" in response.data


def test_login_valid(app, client):
    client.post('/signup', data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "akronohio",
                                 "confirm_password": "akronohio"})
    response = client.post('/login', data={"email": "lebron@gmail.com", "password": "akronohio"})
    assert response.status_code == 302
    assert response.headers['Location'] == "/home"


def test_login_invalid(app, client):
    client.post('/signup', data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "akronohio",
                                 "confirm_password": "akronohio"})
    # wrong password for login
    response = client.post('/login', data={"email": "lebron@gmail.com", "password": "randompass"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data

    # nonexistent email
    response = client.post('/login', data={"email": "bademail@gmail.com", "password": "akronohio"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data

    # empty email field
    response = client.post('/login', data={"email": "", "password": "akronohio"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data


def test_login_with_next(client, auth):
    # check if user is led to page attempted to access without login
    with client.application.test_request_context():
        auth.create()
        response = client.get("/home")
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fhome"

        response = client.post("/login?next=/home", data={"email": "lebron@gmail.com", "password": "akronohio"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/home"


def test_home(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.get('/home')
        assert response.status_code == 200
        assert current_user.is_authenticated
        assert b"<title>Loonie Ledger - Home</title>" in response.data


def test_home_redirect(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.get('/')
        assert response.status_code == 302
        assert response.headers['Location'] == "/home"


def test_welcome_redirect(client, auth):
    with client.application.test_request_context():
        auth.create()
        response = client.get('/')
        assert response.status_code == 302
        assert response.headers['Location'] == "/welcome"


def test_profile_get(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.get('/profile')
        assert response.status_code == 200
        assert current_user.is_authenticated
        assert b"<title>Loonie Ledger - Profile</title>" in response.data


def test_profile_get_not_auth(client, auth):
    response = client.get('/profile')
    assert response.status_code == 302
    assert response.headers['Location'] == "/login?next=%2Fprofile"


def test_profile_update(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.post('/profile', data={"name": "LeBron James Jr", "email": "lebron@gmail.com"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.name == "LeBron James Jr"

        response = client.post('/profile', data={"name": "LeBron James Jr", "email": "lebronjames@gmail.com"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.email == "lebronjames@gmail.com"


def test_profile_update_not_auth(app, client, auth):
    # updating profile without login
    client.post('/signup',
                data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                      "confirm_password": "testpassword"})
    response = client.post('/profile', data={"name": "LeBron James Jr", "email": "lebronjames@gmail.com"})
    assert response.status_code == 302
    assert response.headers['Location'] == "/login?next=%2Fprofile"
    with app.app_context():
        assert User.query.first().name == "LeBron James"
        assert User.query.first().email == "lebron@gmail.com"


def test_profile_update_invalid(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        # updating to existing email johndoe
        response = client.post('/profile',
                               data={"name": "LeBron James", "email": "johndoe@gmail.com"})  # johndoe already exists
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Profile</title>" in response.data
        assert b"That email already exists" in response.data
        assert current_user.email == "lebron@gmail.com"
        response = client.post('/profile',
                               data={"name": "thisisastringwith41charactersblahblahblah",
                                     "email": "lebron@gmail.com"})  # johndoe already exists
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Profile</title>" in response.data
        assert current_user.name == "LeBron James"


def test_profile_update_year(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.post('/profile/update/year', data={"year": 2009})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.year_eligible == 2009

        client.post('/profile/update/year', data={"year": 2100})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.year_eligible == 2100


def test_profile_update_year_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        # not logged in
        response = client.post('/profile/update/year', data={"year": 2015})
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fprofile%2Fupdate%2Fyear"
        with app.app_context():
            assert User.query.first().year_eligible is None


def test_profile_update_year_invalid(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.post('/profile/update/year', data={"year": 2101})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.year_eligible is None

        response = client.post('/profile/update/year', data={"year": 2008})
        assert response.status_code == 302
        assert response.headers['Location'] == "/profile"
        assert current_user.year_eligible is None


def test_settings_get(client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.get('/settings')
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Settings" in response.data


def test_logout(client, auth):
    with client.application.test_request_context():
        auth.create()
        response = auth.login()
        assert response.status_code == 302
        assert response.headers['Location'] == "/home"
        response = client.get('/logout')
        assert response.status_code == 302
        assert response.headers['Location'] == "/welcome"

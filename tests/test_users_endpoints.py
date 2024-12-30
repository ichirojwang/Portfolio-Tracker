from flask_login import current_user

from tests.conftest import AuthActions
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


def test_signup_confirm_password_fail(app, client):
    response = client.post('/signup',
                           data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                                 "confirm_password": "badpassword"})
    with app.app_context():
        assert User.query.count() == 0
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Sign Up</title>" in response.data


def test_signup_empty_fields(app, client):
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


def test_login_valid(app, client):
    client.post('/signup', data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "akronohio",
                                 "confirm_password": "akronohio"})
    response = client.post('/login', data={"email": "lebron@gmail.com", "password": "akronohio"})
    assert response.status_code == 302
    assert response.headers['Location'] == "/home"


def test_login_invalid(app, client):
    client.post('/signup', data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "akronohio",
                                 "confirm_password": "akronohio"})
    response = client.post('/login', data={"email": "lebron@gmail.com", "password": "randompass"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data

    response = client.post('/login', data={"email": "bademail@gmail.com", "password": "akronohio"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data

    response = client.post('/login', data={"email": "", "password": "akronohio"})
    assert response.status_code == 200
    assert b"<title>Loonie Ledger - Log In</title>" in response.data


def test_login_with_next(client, auth):
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
        response = client.post('/profile',
                               data={"name": "LeBron James", "email": "johndoe@gmail.com"})  # johndoe already exists
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Profile</title>" in response.data
        assert current_user.email == "lebron@gmail.com"


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
    client.post('/signup',
                data={"name": "LeBron James", "email": "lebron@gmail.com", "password": "testpassword",
                      "confirm_password": "testpassword"})
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

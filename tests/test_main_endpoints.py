from flask import url_for


def test_home(app, client):
    response = client.get("/welcome", follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Loonie Ledger - Welcome</title>' in response.data
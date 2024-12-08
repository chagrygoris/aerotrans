from unittest.mock import Mock
def test_register_user_success(client):
    response = client.post("/sign_up", data={
        "name": "Test User",
        "email": "test@testov.com",
        "password": "password123"
    })
    assert response.status_code == 303
    assert response.headers["location"] == "/sign_up/tg"


def test_register_user_existing_email(client, mock_session):
    mock_session.query().filter_by().first.return_value = Mock()

    response = client.post("/sign_up", data={
        "name": "Test User",
        "email": "existing@test.com",
        "password": "password123"
    })

    assert response.status_code == 303


def test_login_invalid_credentials(client, mock_session):
    mock_session.query().filter_by().first.return_value = None

    response = client.post("/login", data={
        "email": "wrong@test.com",
        "password": "wrongpass"
    })

    assert response.status_code == 401


def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 307
    assert response.headers["location"] == "/"


def test_search_form_redirect_if_not_authenticated(client):
    response = client.get("/search")
    assert response.status_code == 303
    assert response.headers["location"] == "/"

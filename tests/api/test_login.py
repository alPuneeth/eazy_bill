from tests.factories.user import create_user
from app.core.security import get_password_hash


def test_login_success(client, session):
    """
    Verify that a user with valid credentials can successfully log in.

    Asserts:
    - HTTP 200 response
    - Access token is returned
    - Token type is 'bearer'
    - last_login_at is updated in the database
    """

    password = "Secret@123"

    user = create_user(session, phone="9999999999")
    user.hashed_password = get_password_hash(password)

    session.add(user)
    session.commit()

    payload = {
        "phone": "9999999999",
        "password": password
    }

    response = client.post("/auth/", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] is not None

    session.refresh(user)
    assert user.last_login_at is not None


def test_login_wrong_password(client, session):
    """
    Verify that login fails when password is incorrect.

    Asserts:
    - HTTP 401 response
    - Proper error message
    - last_login_at is NOT updated
    """

    correct_password = "Secret@321"
    wrong_password = "Reveal#123"

    user = create_user(session, phone="9999999990")
    user.hashed_password = get_password_hash(correct_password)

    session.add(user)
    session.commit()

    payload = {
        "phone": "9999999990",
        "password": wrong_password
    }

    response = client.post("/auth/", json=payload)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid credentials"

    session.refresh(user)
    assert user.last_login_at is None


def test_login_inactive_user(client, session):
    """
    Verify that inactive users cannot log in.

    Asserts:
    - HTTP 403 response
    - Proper error message
    - last_login_at is NOT updated
    """
    password = "secret123"

    user = create_user(session, is_active=False)
    user.hashed_password = get_password_hash(password)

    session.add(user)
    session.commit()

    payload = {
        "phone": user.phone,
        "password": password
    }

    response = client.post("/auth/", json=payload)
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Inactive user"

    session.refresh(user)
    assert user.last_login_at is None


def test_login_user_not_found(client, session):
    """
    Verify that login fails when the user does not exist.

    Asserts:
    - HTTP 401 response
    - Proper error message
    """
    payload = {
        "phone": "8888888888",  # valid format, but not in DB
        "password": "anypassword"
    }

    response = client.post("/auth/", json=payload)
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid credentials"

    
from sqlmodel import select

from app.models.core_models.user import User
from tests.factories.user import create_user


def test_login_success(client, session):
    """
    Verify that a user with valid credentials can successfully log in.

    Asserts:
    - HTTP 200 response
    - Access token is returned
    - Token type is 'bearer'
    - last_login_at is updated in the database
    """

    from app.core.security import get_password_hash

    password = "secret123"

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
    """
    from app.core.security import get_password_hash

    correct_password = "secret321"
    wrong_password = "reveal123"

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
    
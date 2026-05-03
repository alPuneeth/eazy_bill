import uuid

from app.models.core_models.user import UserRole
from tests.factories.user import create_agent


def test_create_user_success(client):
    """
    Verify that a new agent user can be created successfully.
    """
    payload = {
        "name": "Agent User",
        "phone": "9876543210",
        "password": "Secret@123",
        "role": UserRole.AGENT.value,
        "user_code": "EEE"
    }

    response = client.post("/user/create", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["role"] == UserRole.AGENT.value


def test_create_user_duplicate_phone(client, session):
    """
    Verify that creating a user with a duplicate phone number returns 409.
    """
    agent = create_agent(session)

    payload = {
        "name": "Agent User",
        "phone": agent.phone,
        "password": "Secret@123",
        "role": UserRole.AGENT.value,
        "user_code": "ETE"
    }

    response = client.post("/user/create", json=payload)

    assert response.status_code == 409


def test_get_user_success(client, session):
    """
    Verify that a user can be fetched by public_id.
    """
    agent = create_agent(session)
    
    response = client.get(f"/user/{agent.public_id}")
    assert response.status_code == 200
    assert response.json()["public_id"] == agent.public_id
    assert response.json()["name"] == agent.name


def test_get_user_not_found(client):
    """
    Verify that fetching a non-existent user returns 404.
    """
    agent_public_id = str(uuid.uuid4())
    response = client.get(f"/user/{agent_public_id}")

    assert response.status_code == 404


def test_update_user_success(client, session):
    """
    Verify that a user's details can be updated successfully.
    """
    agent = create_agent(session)

    payload = {
        "name": "Agent Renamed"
    }

    response = client.patch(f"/user/update/{agent.public_id}", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == payload["name"]


def test_update_user_not_found(client):
    """
    Verify that updating a non-existent user returns 404.
    """
    payload = {"name": "Does not matter"}
    response = client.patch(f"/user/update/{str(uuid.uuid4())}", json=payload)
    assert response.status_code == 404


def test_update_user_duplicate_phone(client, session):
    """
    Verify that updating a user with a phone number already in use returns 409.
    """
    agent1 = create_agent(session)
    agent2 = create_agent(session)

    payload = {"phone": agent1.phone}

    response = client.patch(f"/user/update/{agent2.public_id}", json=payload)
    assert response.status_code == 409
from sqlmodel import select
from app.models.lookup.village import Village
from tests.factories.user import create_agent
from tests.factories.village import create_village

# POST endpoint
def test_assign_villages_to_agent(client, session):
    """
    Verify that unassigned villages can be successfully assigned to an agent.
    Asserts API response and confirms DB state is updated correctly.
    """

    v1 = create_village(session)
    v2 = create_village(session)

    agent = create_agent(session)

    payload = {
        "village_ids": [v1.id, v2.id],
        "force": False
    }

    response = client.post(
        f"/agent/{agent.public_id}/villages",
        json=payload
    )

    data = response.json()

    assert response.status_code == 200
    assert len(data["assigned"]) == 2
    assert data["already_assigned"] == []

    villages = session.exec(
        select(Village).where(Village.id.in_([v1.id, v2.id]))
        ).all()

    for v in villages:
        assert v.agent_id == agent.id


def test_assign_villages_to_agent_duplicate(client, session):
    """
    Verify that reassigning already assigned villages does not duplicate assignment.
    Ensures villages are reported under 'already_assigned'.
    """

    agent =  create_agent(session) 

    v1 = create_village(session)

    payload = {"village_ids": [v1.id], "force": False}

    # first call
    client.post(f"/agent/{agent.public_id}/villages", json=payload)

    # second call
    response = client.post(f"/agent/{agent.public_id}/villages", json=payload)

    data = response.json()

    assert response.status_code == 200
    assert len(data["assigned"]) == 0
    assert data["already_assigned"][0] == v1.id


def test_assign_villages_conflict(client, session):
    """
    Verify that assigning a village owned by another agent fails when force=False.
    Expects a 400 response with an appropriate error message.
    """

    agent1 = create_agent(session)
    agent2 = create_agent(session)

    v1 = create_village(session, agent=agent1)

    payload = {"village_ids": [v1.id], "force": False}

    response = client.post(f"/agent/{agent2.public_id}/villages", json=payload)

    assert response.status_code == 400
    assert "already assigned" in response.json()["message"].lower()


def test_assign_villages_force(client, session):
    """
    Verify that force=True reassigns a village from one agent to another.
    Confirms both API response and updated DB ownership.
    """
    agent1 = create_agent(session)
    agent2 = create_agent(session)

    v1 = create_village(session, agent=agent1) 

    payload = {"village_ids": [v1.id], "force": True}

    response = client.post(f"/agent/{agent2.public_id}/villages", json=payload)

    assert response.status_code == 200
    
    data = response.json()
    assert len(data["assigned"]) == 1

    updated_village = session.exec(
        select(Village).where(Village.id == v1.id)
        ).one()

    assert updated_village.agent_id == agent2.id


# PUT endpoint
def test_replace_villages_success(client, session):
    """
    Verify that existing villages are replaced with new ones.

    Asserts:
    - Old villages are unassigned
    - New villages are assigned
    """
    # set up agent
    agent = create_agent(session)

    # existing villages - agent is assigned
    v1 = create_village(session, agent=agent)
    v2 = create_village(session, agent=agent)

    # new villages - unassigned villages
    v3 = create_village(session)
    v4 = create_village(session)

    # prepare payload
    payload = {
        "village_ids": [v3.id, v4.id]
    }

    # make API call
    response = client.put(
        f"/agent/{agent.public_id}/villages",
        json=payload
        )
    
    assert response.status_code == 200

    # DB verification
    villages = session.exec(
        select(Village)
    ).all()

    # validate state
    for v in villages:
        # assinged to agent
        if v.id in [v3.id, v4.id]:
            assert v.agent_id == agent.id
        
        # unassigned now
        elif v.id in [v1.id, v2.id]:
            assert v.agent_id is None


def test_replace_villages_empty(client, session):
    """
    Verify that replacing with an empty list removes all village assignments.
    """
    agent = create_agent(session)

    v1 = create_village(session, agent=agent)

    payload = {"village_ids": []}

    response = client.put(
        f"/agent/{agent.public_id}/villages",
        json=payload
    )

    assert response.status_code == 200

    updated = session.exec(
        select(Village).where(Village.id == v1.id)
    ).one()

    assert updated.agent_id is None


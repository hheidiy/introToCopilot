import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the global activities dict to its original state after every test."""
    # Arrange (shared): snapshot current state
    original = copy.deepcopy(activities)
    yield
    # Teardown: restore state so tests never bleed into each other
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Arrange — no specific setup needed; default data is sufficient

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_activities():
    # Arrange — no specific setup needed; rely on seeded data

    # Act
    data = client.get("/activities").json()

    # Assert
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_includes_expected_fields():
    # Arrange — no specific setup needed

    # Act
    data = client.get("/activities").json()

    # Assert
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant_to_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400():
    # Arrange — "michael@mergington.edu" is already seeded in Chess Club
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Unknown Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange — "michael@mergington.edu" is seeded in Chess Club
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant_from_activity():
    # Arrange — "michael@mergington.edu" is seeded in Chess Club
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_not_signed_up_returns_404():
    # Arrange
    email = "notregistered@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404

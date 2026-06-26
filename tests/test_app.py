from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

DEFAULT_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(DEFAULT_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_default_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == DEFAULT_ACTIVITIES


def test_signup_for_activity_adds_participant(client):
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 201
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Soccer Team"}
    assert "newstudent@mergington.edu" in activities["Soccer Team"]["participants"]


def test_signup_for_activity_duplicate_returns_409(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_returns_success(client):
    response = client.delete(
        "/activities/Gym Class/participants",
        params={"email": "john@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed john@mergington.edu from Gym Class"}
    assert "john@mergington.edu" not in activities["Gym Class"]["participants"]


def test_remove_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Drama Club/participants",
        params={"email": "absent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

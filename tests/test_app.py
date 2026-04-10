
import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.data import activities
import random
import copy

client = TestClient(app)

# Copie de l'état initial des activités
INITIAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Réinitialise la base d'activités avant chaque test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))

def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)

def test_signup_and_unregister():
    # Arrange
    test_email = f"testuser_{random.randint(1000,9999)}@mergington.edu"
    activity = "Soccer Team"
    from src.data import activities
    from src.app import signup_for_activity_logic, unregister_from_activity_logic, HTTPException
    activities[activity]["participants"] = []

    # Act: signup
    result_signup = signup_for_activity_logic(activity, test_email)
    # Assert
    assert f"Signed up {test_email}" in result_signup["message"]

    # Act: signup again (should fail)
    try:
        signup_for_activity_logic(activity, test_email)
        assert False, "Should have raised HTTPException for duplicate signup"
    except HTTPException as e:
        assert e.status_code == 400

    # Act: unregister
    result_unreg = unregister_from_activity_logic(activity, test_email)
    assert f"Unregistered {test_email}" in result_unreg["message"]

    # Act: unregister again (should fail)
    try:
        unregister_from_activity_logic(activity, test_email)
        assert False, "Should have raised HTTPException for unregistering non-registered"
    except HTTPException as e:
        assert e.status_code == 404

def test_signup_activity_not_found():
    # Arrange
    test_email = "nouser@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"

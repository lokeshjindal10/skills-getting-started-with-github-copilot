import uuid

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = f"testuser+{uuid.uuid4().hex}@example.com"

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200, resp.text
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant was added
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200, resp.text
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_signup_existing_returns_400():
    activity = "Chess Club"
    # pick a participant that already exists in the sample data
    existing = activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    email = f"nonexistent+{uuid.uuid4().hex}@example.com"
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404

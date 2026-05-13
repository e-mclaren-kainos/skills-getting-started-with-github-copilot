import pytest


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

    chess = data["Chess Club"]
    assert {"description", "schedule", "max_participants", "participants"}.issubset(chess.keys())
    assert isinstance(chess["participants"], list)


def test_signup_successfully_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_duplicate_is_rejected(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity_returns_404(client):
    response = client.post("/activities/Not A Real Club/signup", params={"email": "new@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_nonexistent_activity_returns_404(client):
    response = client.delete("/activities/Not A Real Club/participants", params={"email": "any@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404(client):
    response = client.delete("/activities/Chess Club/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


@pytest.mark.xfail(reason="Backend does not enforce activity capacity yet", strict=True)
def test_signup_rejects_when_activity_is_full(client):
    full_activity = "Chess Club"

    # Fill activity to max (12 participants).
    for i in range(10):
        response = client.post(
            f"/activities/{full_activity}/signup",
            params={"email": f"extra{i}@mergington.edu"},
        )
        assert response.status_code == 200

    # One more should be rejected once capacity validation exists.
    overflow_response = client.post(
        f"/activities/{full_activity}/signup",
        params={"email": "overflow@mergington.edu"},
    )

    assert overflow_response.status_code in (400, 409)


@pytest.mark.xfail(reason="Backend does not validate email format yet", strict=True)
def test_signup_rejects_invalid_email_format(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "invalid-email"})

    assert response.status_code in (400, 422)


@pytest.mark.xfail(reason="Backend does not reject empty email yet", strict=True)
def test_signup_rejects_empty_email(client):
    response = client.post("/activities/Chess Club/signup", params={"email": ""})

    assert response.status_code in (400, 422)

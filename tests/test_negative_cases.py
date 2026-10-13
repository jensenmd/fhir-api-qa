"""Malformed input must yield structured errors; accepted data is cleaned up."""
import uuid


def assert_outcome(response, statuses):
    assert response.status_code in statuses, f"{response.status_code} {response.text[:300]}"
    body = response.json()
    assert body["resourceType"] == "OperationOutcome"
    assert any(issue.get("severity") in ("error", "fatal") for issue in body.get("issue", []))


def test_create_patient_with_invalid_birthdate_rejected(create_patient, unique_patient):
    unique_patient["birthDate"] = "not-a-date"
    assert_outcome(create_patient(unique_patient), (400, 422))


def test_read_nonexistent_patient_returns_404(client):
    assert_outcome(client.read("Patient", str(uuid.uuid4())), (404,))


def test_create_with_unknown_resource_type_rejected(client):
    assert_outcome(client.create({"resourceType": "NotARealResource"}), (400, 404))

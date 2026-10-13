"""Negative cases: malformed input must produce OperationOutcome errors,
not 500s or silent acceptance.
"""


def test_create_patient_with_invalid_birthdate_rejected(client):
    resp = client.create({"resourceType": "Patient", "birthDate": "not-a-date"})
    assert resp.status_code in (400, 422), f"got {resp.status_code}"
    body = resp.json()
    assert body["resourceType"] == "OperationOutcome"


def test_read_nonexistent_patient_returns_404(client):
    resp = client.read("Patient", "00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404, f"got {resp.status_code}"


def test_create_with_unknown_resource_type_rejected(client):
    resp = client.create({"resourceType": "NotARealResource"})
    assert resp.status_code in (400, 404), f"got {resp.status_code}"

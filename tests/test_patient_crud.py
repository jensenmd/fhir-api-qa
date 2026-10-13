"""Each lifecycle test owns unique synthetic data and fixture cleanup."""
from utils.patient_search import find_patient


def test_create_patient_returns_201_with_id(create_patient, unique_patient):
    response = create_patient(unique_patient)
    assert response.status_code == 201, f"{response.status_code} {response.text[:300]}"
    body = response.json()
    assert body["resourceType"] == "Patient"
    assert body.get("id")
    assert body["identifier"] == unique_patient["identifier"]


def test_read_patient_round_trip(client, created_patient, unique_patient):
    response = client.read("Patient", created_patient)
    assert response.status_code == 200, f"{response.status_code} {response.text[:300]}"
    body = response.json()
    assert body["resourceType"] == "Patient"
    assert body["id"] == created_patient
    for field in ("identifier", "name", "gender", "birthDate"):
        assert body[field] == unique_patient[field]


def test_update_patient_persists_changes(client, created_patient, unique_patient):
    response = client.read("Patient", created_patient)
    assert response.status_code == 200
    patient = response.json()
    patient["birthDate"] = "1985-05-05"
    updated = client.update(patient)
    assert updated.status_code == 200, f"{updated.status_code} {updated.text[:300]}"
    reread = client.read("Patient", created_patient)
    assert reread.status_code == 200, f"{reread.status_code} {reread.text[:300]}"
    body = reread.json()
    assert body["resourceType"] == "Patient"
    assert body["id"] == created_patient
    assert body["birthDate"] == "1985-05-05"
    assert body["identifier"] == unique_patient["identifier"]


def test_search_finds_created_patient(client, created_patient, unique_patient):
    find_patient(client, created_patient, unique_patient["identifier"][0])


def test_delete_patient_removes_resource(client, created_patient):
    response = client.delete("Patient", created_patient)
    assert response.status_code in (200, 204), f"{response.status_code} {response.text[:300]}"
    reread = client.read("Patient", created_patient)
    assert reread.status_code in (404, 410), f"got {reread.status_code}"

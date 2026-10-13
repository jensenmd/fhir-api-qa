"""Patient CRUD lifecycle: create -> read -> update -> search -> delete.

Each test creates its own Patient with a unique identifier and cleans up,
so the suite is safe against the shared public HAPI server.
"""


def test_create_patient_returns_201_with_id(client, unique_patient):
    resp = client.create(unique_patient)
    assert resp.status_code == 201, f"{resp.status_code} {resp.text[:300]}"
    body = resp.json()
    assert body["resourceType"] == "Patient"
    assert body.get("id")
    client.delete("Patient", body["id"])


def test_read_patient_round_trip(client, created_patient, unique_patient):
    resp = client.read("Patient", created_patient)
    assert resp.status_code == 200, f"{resp.status_code} {resp.text[:300]}"
    body = resp.json()
    assert body["id"] == created_patient
    assert body["name"][0]["family"] == unique_patient["name"][0]["family"]
    assert body["birthDate"] == unique_patient["birthDate"]


def test_update_patient_persists_changes(client, created_patient):
    resp = client.read("Patient", created_patient)
    assert resp.status_code == 200
    patient = resp.json()
    patient["birthDate"] = "1985-05-05"
    upd = client.update(patient)
    assert upd.status_code == 200, f"{upd.status_code} {upd.text[:300]}"
    assert upd.json()["birthDate"] == "1985-05-05"


def test_search_finds_created_patient(client, created_patient, unique_patient):
    family = unique_patient["name"][0]["family"]
    resp = client.search("Patient", {"family": family})
    assert resp.status_code == 200, f"{resp.status_code} {resp.text[:300]}"
    bundle = resp.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle["total"] >= 1
    ids = [e["resource"]["id"] for e in bundle.get("entry", [])]
    assert created_patient in ids


def test_delete_patient_removes_resource(client, unique_patient):
    resp = client.create(unique_patient)
    assert resp.status_code == 201
    pid = resp.json()["id"]
    del_resp = client.delete("Patient", pid)
    assert del_resp.status_code in (200, 204), (
        f"{del_resp.status_code} {del_resp.text[:300]}"
    )
    get_resp = client.read("Patient", pid)
    # HAPI FHIR returns 410 Gone for deleted resources
    assert get_resp.status_code in (404, 410), f"got {get_resp.status_code}"

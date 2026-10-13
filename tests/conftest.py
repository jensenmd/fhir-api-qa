"""Shared fixtures: one client per session, unique test data per test."""
import uuid

import pytest

from utils.fhir_client import FhirClient


@pytest.fixture(scope="session")
def client():
    return FhirClient()


@pytest.fixture
def unique_patient():
    """A Patient payload with a unique identifier so tests never collide,
    even against the shared public server."""
    tag = uuid.uuid4().hex[:8]
    return {
        "resourceType": "Patient",
        "identifier": [
            {"system": "http://qa-demo.example/fhir-api-qa", "value": f"test-{tag}"}
        ],
        "name": [{"family": "QADemo", "given": [f"Test{tag}"]}],
        "gender": "unknown",
        "birthDate": "1990-01-01",
    }


@pytest.fixture
def created_patient(client, unique_patient):
    """Creates a Patient, yields its id, then deletes it (best effort)."""
    resp = client.create(unique_patient)
    assert resp.status_code == 201, f"setup failed: {resp.status_code} {resp.text[:300]}"
    patient_id = resp.json()["id"]
    yield patient_id
    client.delete("Patient", patient_id)

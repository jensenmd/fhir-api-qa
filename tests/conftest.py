"""Unique synthetic Patients with cleanup registered before test assertions."""
import os
import uuid

import pytest

from utils.fhir_client import FhirClient
from utils.patient_cleanup import PatientCleanup


@pytest.fixture(scope="session")
def client():
    instance = FhirClient(base_url=os.environ.get("FHIR_BASE_URL", "https://hapi.fhir.org/baseR4"))
    yield instance
    instance.session.close()


@pytest.fixture
def unique_patient():
    tag = uuid.uuid4().hex
    return {
        "resourceType": "Patient",
        "identifier": [{"system": "http://qa-demo.example/fhir-api-qa", "value": f"test-{tag}"}],
        "name": [{"family": "QADemo", "given": [f"Test{tag}"]}],
        "gender": "unknown",
        "birthDate": "1990-01-01",
    }


@pytest.fixture
def create_patient(client):
    cleanup = PatientCleanup(client)
    yield cleanup.create
    cleanup.finish()


@pytest.fixture
def created_patient(create_patient, unique_patient):
    response = create_patient(unique_patient)
    assert response.status_code == 201, f"setup failed: {response.status_code} {response.text[:300]}"
    body = response.json()
    assert body["resourceType"] == "Patient"
    assert body.get("id")
    return body["id"]

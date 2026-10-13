"""Smoke tests: the server is up and declares FHIR R4 capabilities.

These run first and fail fast if the server is unreachable or misconfigured.
"""


def test_capability_statement_returns_fhir_json(client):
    cs = client.get_capability_statement()
    assert cs["resourceType"] == "CapabilityStatement"


def test_server_declares_r4(client):
    cs = client.get_capability_statement()
    assert cs.get("fhirVersion", "").startswith("4."), (
        f"expected FHIR R4, got {cs.get('fhirVersion')}"
    )


def test_server_supports_patient_resource(client):
    cs = client.get_capability_statement()
    resources = [r["type"] for r in cs["rest"][0]["resource"]]
    assert "Patient" in resources

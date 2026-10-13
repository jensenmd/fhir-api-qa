"""Selected smoke checks run first and stop the suite on failure."""
import pytest

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def capabilities(client):
    return client.get_capability_statement()


def test_capability_statement_returns_fhir_json(capabilities):
    assert capabilities["resourceType"] == "CapabilityStatement"


def test_server_declares_r4(capabilities):
    assert capabilities.get("fhirVersion") == "4.0.1", f"expected R4 4.0.1, got {capabilities.get('fhirVersion')}"


def test_server_supports_patient_resource(capabilities):
    patients = [resource for rest in capabilities.get("rest", []) if rest.get("mode") == "server"
                for resource in rest.get("resource", []) if resource.get("type") == "Patient"]
    assert patients, "No server-mode Patient capability"
    supported = {interaction["code"] for resource in patients for interaction in resource.get("interaction", [])}
    assert {"create", "read", "update", "delete", "search-type"} <= supported
    assert any(p.get("name") == "identifier" and p.get("type") == "token"
               for resource in patients for p in resource.get("searchParam", []))

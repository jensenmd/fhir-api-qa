"""Retry only valid, empty search results while the server indexes a write."""
import time


def find_patient(client, patient_id, identifier, attempts=10, interval=2, sleep=time.sleep):
    assert attempts >= 1
    token = f"{identifier['system']}|{identifier['value']}"
    for attempt in range(attempts):
        response = client.search("Patient", {"identifier": token})
        assert response.status_code == 200, f"search: {response.status_code} {response.text[:300]}"
        bundle = response.json()
        assert bundle.get("resourceType") == "Bundle"
        assert bundle.get("type") == "searchset"
        matches = []
        for entry in bundle.get("entry", []):
            # OperationOutcome entries are not search matches; fail on error diagnostics.
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "OperationOutcome":
                assert not any(i.get("severity") in ("error", "fatal") for i in resource.get("issue", [])), resource
                continue
            assert resource.get("resourceType") == "Patient", resource
            assert identifier in resource.get("identifier", []), "Search returned an unrelated Patient"
            matches.append(resource)
        if matches:
            assert len(matches) == 1 and matches[0].get("id") == patient_id, "Search returned unexpected IDs"
            return matches[0]
        assert not any(link.get("relation") == "next" for link in bundle.get("link", [])), "Unexpected pagination for unique identifier"
        if attempt + 1 < attempts:
            sleep(interval)
    raise AssertionError(f"Patient/{patient_id} absent after {attempts} identifier searches")

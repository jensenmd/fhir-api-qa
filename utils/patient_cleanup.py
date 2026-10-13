"""Track returned Patient IDs before callers assert on creation responses."""
import re


class PatientCleanup:
    def __init__(self, client):
        self.client = client
        self.ids = set()

    def create(self, payload):
        response = self.client.create(payload)
        # A server unexpectedly accepting a negative payload still needs cleanup.
        if 200 <= response.status_code < 300:
            location = response.headers.get("Location", "")
            match = re.search(r"(?:^|/)Patient/([A-Za-z0-9.-]{1,64})(?:/_history/[^/]+)?/?$", location)
            if match:
                self.ids.add(match.group(1))
            try:
                body = response.json()
            except ValueError:
                body = {}
            if isinstance(body, dict) and body.get("resourceType") == "Patient" and body.get("id"):
                self.ids.add(body["id"])
            assert match or (isinstance(body, dict) and body.get("resourceType") == "Patient" and body.get("id")), (
                "Successful create returned no Patient ID or Location; cannot guarantee cleanup"
            )
        return response

    def finish(self):
        errors = []
        for patient_id in sorted(self.ids):
            try:
                response = self.client.delete("Patient", patient_id)
                if response.status_code not in (200, 204, 404, 410):
                    errors.append(f"Patient/{patient_id}: DELETE {response.status_code} {response.text[:200]}")
            except Exception as exc:
                errors.append(f"Patient/{patient_id}: {exc}")
        assert not errors, "Cleanup failed: " + "; ".join(errors)

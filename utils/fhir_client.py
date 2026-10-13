"""Thin wrapper around a FHIR R4 server.

Defaults to the public HAPI FHIR test server. Every test creates its own
data and cleans up after itself, since the public server is shared.
"""
import requests

BASE_URL = "https://hapi.fhir.org/baseR4"


class FhirClient:
    def __init__(self, base_url=BASE_URL, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            }
        )

    def _url(self, path):
        return f"{self.base_url}/{path.lstrip('/')}"

    def get_capability_statement(self):
        r = self.session.get(self._url("metadata"), timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def create(self, resource):
        return self.session.post(
            self._url(resource["resourceType"]), json=resource, timeout=self.timeout
        )

    def read(self, resource_type, resource_id):
        return self.session.get(
            self._url(f"{resource_type}/{resource_id}"), timeout=self.timeout
        )

    def update(self, resource):
        return self.session.put(
            self._url(f"{resource['resourceType']}/{resource['id']}"),
            json=resource,
            timeout=self.timeout,
        )

    def delete(self, resource_type, resource_id):
        return self.session.delete(
            self._url(f"{resource_type}/{resource_id}"), timeout=self.timeout
        )

    def search(self, resource_type, params):
        return self.session.get(
            self._url(resource_type), params=params, timeout=self.timeout
        )

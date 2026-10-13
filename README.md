# fhir-api-qa

Quality engineering for HL7 FHIR R4 APIs, demonstrated against the public
[HAPI FHIR](https://hapi.fhir.org/) test server.

## What's covered

| Layer | Tests |
|---|---|
| Server capabilities | CapabilityStatement smoke tests, R4 conformance, Patient support |
| Patient CRUD | Create, read (round-trip), update, search, delete lifecycle |
| Negative cases | Malformed input rejected with `OperationOutcome`, never 500s |

## Design notes

- **Every test creates its own data** with a unique identifier and deletes it
  afterwards. The public HAPI server is shared, so tests must never depend
  on pre-existing data or collide with each other.
- **Layered assertions**: HTTP status first, then `resourceType`, then
  field-level round-trip integrity.
- **Negative cases assert error contracts**: FHIR servers must return an
  `OperationOutcome` for rejected input.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Roadmap

- Search semantics: chaining, `_include`/`_revinclude`, `_count`, `_sort`, date prefixes
- `$validate` operation and profile conformance
- Observation resource lifecycle with Patient references
- Business rules: identifier uniqueness, must-support elements

# fhir-api-qa

A healthcare API needs to preserve the data it accepts and respond clearly when a request is invalid. This project tests that behavior against the public HAPI FHIR R4 server: capability checks, Patient lifecycle integrity, isolated search, and structured errors, with pytest and retained CI reports.

![CI Status](https://github.com/jensenmd/fhir-api-qa/actions/workflows/ci.yml/badge.svg)

![fhir-api-qa portfolio project card](fhir-api-qa-project-card.png)

Built by **Michael D. Jensen** — Senior QA Engineer with 15+ years of enterprise testing experience, specializing in API testing, automation, and CI/CD-integrated quality practices.

🔗 [LinkedIn](https://www.linkedin.com/in/michaeljensen-qa/) | 📧 jensen.md@gmail.com

---

## What This Project Demonstrates

| Layer | Stack | Coverage |
|---|---|---|
| Server Conformance | pytest + requests | CapabilityStatement validation, FHIR R4 version check, resource support |
| Patient Lifecycle | pytest + requests | Full CRUD: create, read (round-trip), update, search, delete |
| Negative Cases | pytest + requests | Malformed input rejected with `OperationOutcome`, never 500s |
| CI/CD Pipeline | GitHub Actions | Full suite on main pushes/PRs, weekly schedule, and manual dispatch |

The scope is deliberately at the API and data layers: selected field integrity, search behavior, and error contracts. It provides focused evidence about those behaviors; broader clinical workflows and production interoperability need additional validation.

---

## Why HAPI FHIR?

[HAPI FHIR](https://hapi.fhir.org/) is an open-source implementation of HL7 FHIR, maintained by Smile CDR and used across the healthcare industry. Its public test server provides:

- A real FHIR R4 API with the full resource lifecycle (create, read, update, delete, search)
- A CapabilityStatement endpoint declaring exactly what the server supports
- Strict validation behavior — malformed resources are rejected with structured `OperationOutcome` errors
- Enough realism to write meaningful tests without requiring access to a production EHR

The public server makes these checks reproducible without access to a production EHR, while also exposing the latency and indexing behavior of shared infrastructure.

---

## Project Structure

```
fhir-api-qa/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Runs pytest on push/PR + weekly schedule
├── tests/
│   ├── conftest.py                 # Client fixture, unique test data, cleanup
│   ├── test_server_capabilities.py # CapabilityStatement smoke tests
│   ├── test_patient_crud.py        # Patient lifecycle: CRUD + search + delete
│   ├── test_negative_cases.py      # Malformed input, error contracts
│   └── unit/                       # Offline hardening regression checks
├── utils/
│   ├── fhir_client.py              # Thin FHIR R4 client wrapper
│   ├── patient_cleanup.py          # ID tracking and teardown diagnostics
│   └── patient_search.py           # Isolated, bounded indexing wait
├── conftest.py                    # Serial smoke ordering and failure gate
├── pytest.ini                     # Strict markers and test discovery
├── assets/                        # Editable portfolio card source
├── TEST_PLAN.md                    # Test strategy, scope, risk areas
├── requirements.txt
├── fhir-api-qa-project-card.png
└── README.md
```

---

## Test Coverage

### Server Capabilities

| Check | What's Validated |
|---|---|
| CapabilityStatement | Endpoint returns valid FHIR JSON with `resourceType: CapabilityStatement` |
| FHIR version | Server declares FHIR R4 (`fhirVersion` equals `4.0.1`) |
| Resource support | Server-mode Patient create/read/update/delete/search and token identifier search |

These smoke tests run first and stop the remaining selected suite on failure.

### Patient Lifecycle

| Operation | What's Validated |
|---|---|
| Create | `201 Created` with server-assigned id |
| Read | Round-trip integrity — what you wrote is what you read back |
| Update | Changes persist on re-read |
| Search | Exact `identifier=system|value` search finds only the created Patient; bounded indexing wait |
| Delete | Resource removed; subsequent read returns `404`/`410`, never the record |

### Negative Cases

| Input | Expected |
|---|---|
| Invalid `birthDate` (`"not-a-date"`) | `400`/`422` with `OperationOutcome` |
| Read of nonexistent id | `404` |
| Unknown `resourceType` | `400`/`404`, never a `500` |

The error contract matters as much as the happy path. A FHIR server that silently accepts malformed clinical data is a patient-safety issue, not just a test failure.

---

## Test Data Isolation

Every test that creates a Patient uses a full UUID identifier and registers its returned ID for fixture teardown before assertions. This includes unexpectedly accepted invalid Patient payloads. The public HAPI server is shared infrastructure — tests must never depend on pre-existing data, collide with each other, or leave debris behind. Tests own their data and do not rely on execution order. Parallel execution is not configured or verified; the smoke gate applies to the selected tests in a serial pytest run. (See `TEST_PLAN.md` for the full strategy.)

---

## CI/CD Pipeline

GitHub Actions is configured to run on pushes and pull requests to `main`, plus a weekly Monday schedule as a health check:

- **pytest job** — installs pinned dependencies and runs selected smoke tests first. A failed smoke check stops the remaining suite with a nonzero exit. Other failures do not stop unrelated tests.
- **Reports** — JUnit XML and a self-contained HTML report are uploaded with `if: always()` and retained for 14 days, including failing runs that reached pytest.
- **Triggers** — pushes/PRs to `main`, Monday 09:00 UTC, and manual dispatch. The job has a 15-minute timeout; automatic concurrency cancellation is disabled to allow teardown.

> **CI triage:** Smoke checks stop the suite when the server is unavailable or incompatible. Other failures retain response diagnostics and reports for investigation; the suite does not automatically classify their cause or turn them into passes.

---

## Running Locally

### Prerequisites
- Python 3.10+

### Run the suite
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v --junitxml=reports/junit.xml --html=reports/pytest-report.html --self-contained-html
```

Validated locally on Python 3.12.10; CI targets Python 3.12. On Windows, activate with `.venv\Scripts\Activate.ps1`. To run offline regression checks: `python -m pytest -m unit -v`. Set `FHIR_BASE_URL` to use another compatible disposable FHIR R4 server. Running a subset without smoke tests bypasses the gate.

Search retries only valid empty search Bundles (10 attempts, 2 seconds apart); HTTP errors, invalid Bundles, unrelated results, and duplicate matches fail immediately. Each HTTP call has a 30-second timeout; slow requests can extend the indexing wait beyond 18 seconds.

Cleanup attempts every registered ID and reports failures as teardown errors. If the server accepts a write but the connection loses its response, no returned ID is available. Process termination, CI cancellation, or server outages can also prevent cleanup. Use only synthetic data; deletion does not purge server history.

The checks cover selected fields and server behavior, not full FHIR schema validation, clinical safety certification, or production EHR interoperability.

---

## QA Portfolio Quick Reference

See [Michael D. Jensen’s QA portfolio](https://github.com/jensenmd) for the complete project overview.

| Project | Purpose and Approach |
| --- | --- |
| [fhir-api-qa](https://github.com/jensenmd/fhir-api-qa) **(this repository)** | Checks whether a healthcare API preserves Patient data through its lifecycle, with isolated FHIR tests and useful CI failure evidence. |
| [pharmacy-spend-etl-qa](https://github.com/jensenmd/pharmacy-spend-etl-qa) | Checks that pharmacy spend data survives the trip from source files to analytics tables, using SQL reconciliation on a synthetic pipeline. |
| [restful-booker-qa](https://github.com/jensenmd/restful-booker-qa) | Tests booking behavior at both API and browser layers, combining Postman/Newman and Playwright for repeatable regression feedback. |
| [qa-automation-showcase](https://github.com/jensenmd/qa-automation-showcase) | Examines API behavior and the quality of returned data together, using pytest, Postman, and Python validation. |
| [android-appium-wdio-poc](https://github.com/jensenmd/android-appium-wdio-poc) | Builds a focused baseline for Android UI checks, exercising Settings navigation on a local emulator with Appium and WebdriverIO. |
| [mapmyrun-quality-investigation](https://github.com/jensenmd/mapmyrun-quality-investigation) | Investigates how workout tracking affects data integrity and user trust, using mobile field experiments and separating observations from explanations. |
| [ai-qa-framework](https://github.com/jensenmd/ai-qa-framework) | Explores how AI can help develop useful API test coverage while keeping a QA engineer responsible for review and pytest execution. |
| [claude-code-qa-sessions](https://github.com/jensenmd/claude-code-qa-sessions) | Shows how human QA judgment guides Claude Code from finding coverage gaps to making targeted, reviewed test improvements. |
| [agentqa-orchestrator](https://github.com/jensenmd/agentqa-orchestrator) | Explores inspectable AI code reviews, using Gemini and Pydantic-defined response schemas to produce structured JSON audit artifacts. |

---

## Author

**Michael D. Jensen** — Senior QA Engineer
15+ years of enterprise software testing experience across healthcare IT, financial systems, telecommunications, and cybersecurity. Deep background in REST API validation, ETL pipeline testing, SQL-based data integrity verification, and full-stack manual testing in Agile environments.

Current hands-on work includes Python/pytest automation, Playwright UI testing, and CI/CD-integrated quality practices.

🔗 [LinkedIn](https://www.linkedin.com/in/michaeljensen-qa/) | 🐙 [GitHub Profile](https://github.com/jensenmd) | 📧 jensen.md@gmail.com

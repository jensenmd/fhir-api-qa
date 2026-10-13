# fhir-api-qa

A QA portfolio project targeting the public HAPI FHIR R4 test server — the reference implementation of HL7 FHIR, the interoperability standard behind modern healthcare data exchange. This project demonstrates backend API quality engineering for healthcare systems: server conformance checks, resource lifecycle testing, and negative-case validation, all running automatically in CI on every push.

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
| CI/CD Pipeline | GitHub Actions | Full suite runs automatically on every push and PR, plus weekly schedule |

This is a backend-only project by design. FHIR quality lives at the API and data layers — schema conformance, search semantics, and error contracts — so every test targets the layer where healthcare interoperability actually breaks.

---

## Why HAPI FHIR?

[HAPI FHIR](https://hapi.fhir.org/) is the open-source reference implementation of HL7 FHIR, maintained by Smile CDR and used across the healthcare industry. Its public test server provides:

- A real FHIR R4 API with the full resource lifecycle (create, read, update, delete, search)
- A CapabilityStatement endpoint declaring exactly what the server supports
- Strict validation behavior — malformed resources are rejected with structured `OperationOutcome` errors
- Enough realism to write meaningful tests without requiring access to a production EHR

It's the closest thing the QA community has to a standard practice target for healthcare interoperability testing — it behaves like a real clinical data server, including the quirks of shared public infrastructure.

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
│   └── test_negative_cases.py      # Malformed input, error contracts
├── utils/
│   └── fhir_client.py              # Thin FHIR R4 client wrapper
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
| FHIR version | Server declares FHIR R4 (`fhirVersion` starts with `4.`) |
| Resource support | `Patient` is in the server's declared resource list |

These are smoke tests by intent — if the server is down or not R4, nothing downstream runs meaningfully.

### Patient Lifecycle

| Operation | What's Validated |
|---|---|
| Create | `201 Created` with server-assigned id |
| Read | Round-trip integrity — what you wrote is what you read back |
| Update | Changes persist on re-read |
| Search | `family` search returns a Bundle containing the created patient |
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

Every test generates a Patient with a unique identifier and deletes it in fixture teardown. The public HAPI server is shared infrastructure — tests must never depend on pre-existing data, collide with each other, or leave debris behind. A test must pass whether it runs alone, in parallel, or after any other test. (See `TEST_PLAN.md` for the full strategy.)

---

## CI/CD Pipeline

GitHub Actions runs on every push and pull request to `main`, plus a weekly Monday schedule as a health check:

- **pytest job** — installs dependencies, runs the full suite with `-v`, fails the build on any test failure

> **Note on CI stability:** The public HAPI FHIR server is shared infrastructure with variable latency. Timeouts are set generously and capability smoke tests fail fast, so infrastructure issues are distinguishable from test failures — the same triage discipline as any external-dependency pipeline: tests that fail due to upstream instability are categorically different from tests that fail due to application defects.

---

## Running Locally

### Prerequisites
- Python 3.10+

### Run the suite
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

---

## QA Portfolio Quick Reference

This project is part of a broader QA portfolio demonstrating complementary quality-engineering skills.

| Project | Focus |
|---|---|
| [android-appium-wdio-poc](https://github.com/jensenmd/android-appium-wdio-poc) | Native Android UI automation proof of concept using Appium, WebdriverIO, TypeScript, and UiAutomator2 |
| [mapmyrun-quality-investigation](https://github.com/jensenmd/mapmyrun-quality-investigation) | Black-box mobile and GPS quality investigation using field evidence and bounded conclusions |
| [restful-booker-qa](https://github.com/jensenmd/restful-booker-qa) | Layered API and UI automation using Postman, Newman, Playwright, and GitHub Actions |
| [pharmacy-spend-etl-qa](https://github.com/jensenmd/pharmacy-spend-etl-qa) | ETL pipeline and SQL-driven data-integrity validation modeled after healthcare analytics work |
| [qa-automation-showcase](https://github.com/jensenmd/qa-automation-showcase) | REST API testing, data validation, and CI/CD-integrated automation |
| [ai-qa-framework](https://github.com/jensenmd/ai-qa-framework) | Human-reviewed AI-assisted test generation with structured cases and pytest execution |
| [claude-code-qa-sessions](https://github.com/jensenmd/claude-code-qa-sessions) | Agentic analysis of existing QA repositories with human review and targeted implementation |
| [agentqa-orchestrator](https://github.com/jensenmd/agentqa-orchestrator) | Structured agentic code auditing using Python, Pydantic, Gemini, and JSON |
| [fhir-api-qa](https://github.com/jensenmd/fhir-api-qa) **(this repository)** | FHIR R4 API testing with pytest against the public HAPI FHIR server — CapabilityStatement checks, Patient CRUD, negative cases, GitHub Actions CI |

---

## Author

**Michael D. Jensen** — Senior QA Engineer
15+ years of enterprise software testing experience across healthcare IT, financial systems, telecommunications, and cybersecurity. Deep background in REST API validation, ETL pipeline testing, SQL-based data integrity verification, and full-stack manual testing in Agile environments.

Current hands-on work includes Python/pytest automation, Playwright UI testing, and CI/CD-integrated quality practices.

🔗 [LinkedIn](https://www.linkedin.com/in/michaeljensen-qa/) | 🐙 [GitHub Profile](https://github.com/jensenmd) | 📧 jensen.md@gmail.com

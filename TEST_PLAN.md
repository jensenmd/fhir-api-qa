# Test Plan — fhir-api-qa

## Objective and scope
Validate selected FHIR R4 server capabilities, synthetic Patient lifecycle integrity,
isolated identifier search, and structured errors against a disposable public server.
Full schema validation, clinical safety, authentication, performance, other resources,
production EHR interoperability, and parallel execution are outside this scope.

## Execution
Selected `smoke` tests run first in serial pytest and stop remaining tests on the
first setup/call/teardown failure. Metadata must declare R4 4.0.1, server-mode Patient
CRUD/search interactions, and token identifier search. Selecting a subset without
smoke tests bypasses this gate. Non-smoke failures allow other tests to continue.

Five lifecycle tests check creation, selected field round-trip, PUT followed by GET,
unique system|value identifier search, and DELETE followed by a 404/410 read.
Three negative tests require error/fatal OperationOutcome issues for invalid dates,
random nonexistent IDs, and unknown resource types. These are focused behavior
checks, not exhaustive FHIR conformance validation.

## Isolation and cleanup
Patient identifiers use full UUIDs. Tests register IDs from successful create
responses before assertions, with Location fallback for malformed response bodies.
Fixture teardown attempts every registered ID even after assertions fail and reports
cleanup errors. Delete accepts 200/204 or already-absent 404/410 in teardown.
Unexpectedly accepted invalid Patient payloads also enter cleanup.
No pre-existing records are modified. Only synthetic data is used.
Lost create responses, killed processes, cancelled jobs, or unavailable servers can
prevent cleanup; deletion does not purge historical versions. CI does not automatically
cancel an active run on a newer push, but manual cancellation remains possible.

## Search consistency and failure policy
Only valid empty searchset Bundles are retried: 10 attempts with 2-second sleeps.
Every request has a 30-second timeout, so 18 seconds is the sleep budget, not a
total deadline. HTTP errors, malformed Bundles, unrelated Patients, duplicate IDs,
and error/fatal OperationOutcome entries fail immediately. Exhaustion fails the test.
No blanket retries or skips turn infrastructure failures into passes.

## Offline regression coverage
Mocked tests verify delayed indexing, exhaustion, immediate error rejection,
cleanup registration/Location fallback, all-ID cleanup after failures, and pytest's
smoke ordering/failure gate in an isolated subprocess. They require no public server.

## CI evidence and criteria
CI runs the full selected suite on main pushes/PRs, Monday 09:00 UTC, or manual
dispatch, on Python 3.12. JUnit XML and HTML reports are retained for 14 days with
an always-run upload step. Generated reports and caches are ignored by Git.
Entry: metadata reachable and compatible. Exit: full live and offline suite green,
cleanup successful, no dependency on another test's data. Any failure requires
triage of response diagnostics; infrastructure vs. product cause is not auto-classified.

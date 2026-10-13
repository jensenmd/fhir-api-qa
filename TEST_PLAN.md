# Test Plan — fhir-api-qa

## Objective

Demonstrate backend/API quality engineering against a real HL7 FHIR R4
server, with emphasis on data integrity, error contracts, and safe testing
against shared infrastructure.

## Scope

In scope: FHIR R4 Patient resource lifecycle, server capability
conformance, negative input handling.
Out of scope (for now): authentication/authorization, performance,
other resource types — see README roadmap.

## Approach

1. **Smoke first**: CapabilityStatement checks gate the suite. If the server
   is down or not R4, nothing else runs meaningfully.
2. **Lifecycle testing**: each CRUD test owns its data end-to-end, asserting
   round-trip integrity (what you wrote is what you read back).
3. **Negative testing**: the server's error contract matters as much as the
   happy path. Rejected input must yield `OperationOutcome`, never a 500
   or silent acceptance.
4. **Shared-infrastructure safety**: unique identifiers per test, best-effort
   cleanup in fixtures. A test must pass whether it runs alone, in parallel,
   or after any other test.

## Risk areas

- Public test server availability and latency (mitigated: generous timeouts,
  smoke tests fail fast).
- Eventual consistency on search after write (mitigated: search test asserts
  on the created patient's unique family name).
- Delete semantics vary by server (HAPI returns 410 Gone; test accepts
  404/410).

## Entry/exit criteria

- Entry: HAPI FHIR R4 metadata endpoint reachable.
- Exit: full suite green on a clean run, no test depending on another
  test's data.

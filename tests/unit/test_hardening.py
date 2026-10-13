"""Offline regressions for failure paths that are unsafe to induce publicly."""
from pathlib import Path
import os
import subprocess
import sys
from unittest.mock import Mock

import pytest

from utils.patient_cleanup import PatientCleanup
from utils.patient_search import find_patient

pytestmark = pytest.mark.unit
IDENTIFIER = {"system": "urn:test", "value": "unique"}


def response(body, status=200, headers=None):
    result = Mock(status_code=status, text="diagnostic", headers=headers or {})
    result.json.return_value = body
    return result


def bundle(entries=()):
    return {"resourceType": "Bundle", "type": "searchset", "entry": [{"resource": r} for r in entries]}


def patient(pid="owned"):
    return {"resourceType": "Patient", "id": pid, "identifier": [IDENTIFIER]}


def test_search_waits_only_for_empty_results():
    client = Mock()
    client.search.side_effect = [response(bundle()), response(bundle([patient()]))]
    sleep = Mock()
    assert find_patient(client, "owned", IDENTIFIER, sleep=sleep)["id"] == "owned"
    sleep.assert_called_once_with(2)
    client.search.assert_called_with("Patient", {"identifier": "urn:test|unique"})


def test_search_exhaustion_fails():
    client = Mock()
    client.search.return_value = response(bundle())
    sleep = Mock()
    with pytest.raises(AssertionError, match="absent after 3"):
        find_patient(client, "owned", IDENTIFIER, attempts=3, sleep=sleep)
    assert client.search.call_count == 3
    assert sleep.call_count == 2


@pytest.mark.parametrize("result", [
    response(bundle(), 500), response({"resourceType": "OperationOutcome"}),
    response(bundle([{"resourceType": "Patient", "id": "other"}])),
    response(bundle([patient("other")])),
    response(bundle([patient(), patient()])),
    response(bundle([{"resourceType": "OperationOutcome", "issue": [{"severity": "error"}]}])),
])
def test_search_real_errors_fail_without_retry(result):
    client = Mock()
    client.search.return_value = result
    sleep = Mock()
    with pytest.raises(AssertionError):
        find_patient(client, "owned", IDENTIFIER, sleep=sleep)
    assert client.search.call_count == 1
    sleep.assert_not_called()


def test_cleanup_registered_before_caller_assertion():
    client = Mock()
    client.create.return_value = response(patient(), 201)
    client.delete.return_value = response({}, 204)
    cleanup = PatientCleanup(client)
    with pytest.raises(AssertionError):
        try:
            cleanup.create({"resourceType": "Patient"})
            assert False, "simulated caller failure"
        finally:
            cleanup.finish()
    client.delete.assert_called_once_with("Patient", "owned")


def test_location_fallback_handles_invalid_json():
    client = Mock()
    client.create.return_value = response({}, 201, {"Location": "https://example/Patient/owned/_history/1"})
    client.create.return_value.json.side_effect = ValueError("invalid JSON")
    client.delete.return_value = response({}, 204)
    cleanup = PatientCleanup(client)
    cleanup.create({"resourceType": "Patient"})
    cleanup.finish()
    client.delete.assert_called_once_with("Patient", "owned")


def test_cleanup_attempts_all_ids_and_surfaces_failure():
    client = Mock()
    client.create.side_effect = [response(patient("a"), 201), response(patient("b"), 200)]
    client.delete.side_effect = [RuntimeError("offline"), response({}, 500)]
    cleanup = PatientCleanup(client)
    cleanup.create({"resourceType": "Patient"})
    cleanup.create({"resourceType": "Patient"})
    with pytest.raises(AssertionError, match="Cleanup failed") as error:
        cleanup.finish()
    assert client.delete.call_count == 2
    assert "Patient/a" in str(error.value) and "Patient/b" in str(error.value)


def test_smoke_gate_orders_and_stops_subprocess(tmp_path):
    source = Path(__file__).resolve().parents[2] / "conftest.py"
    (tmp_path / "conftest.py").write_text(source.read_text(), encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\nmarkers =\n    smoke: gate\n", encoding="utf-8")
    (tmp_path / "test_gate.py").write_text(
        "import pytest\ndef test_a_lifecycle():\n    assert False, 'LIFECYCLE RAN'\n"
        "@pytest.mark.smoke\ndef test_z_smoke():\n    assert False, 'SMOKE FAILED'\n", encoding="utf-8")
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    env.pop("PYTEST_ADDOPTS", None)
    run = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=tmp_path,
                         env=env, capture_output=True, text=True, timeout=30)
    assert run.returncode != 0
    assert "Smoke gate failed" in run.stdout
    assert "1 failed" in run.stdout
    assert "LIFECYCLE RAN" not in run.stdout

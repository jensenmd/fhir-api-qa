"""Run selected smoke checks first; stop after the first failing smoke check."""
import pytest


def pytest_collection_modifyitems(items):
    items.sort(key=lambda item: item.get_closest_marker("smoke") is None)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed and item.get_closest_marker("smoke"):
        item.session.shouldstop = f"Smoke gate failed: {item.nodeid} ({report.when})"

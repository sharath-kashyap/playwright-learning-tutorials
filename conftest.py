"""
conftest.py

Root-level pytest configuration.

Provides:
  - pytest hooks that record setup / call / teardown durations for every test
  - timed_browser, timed_context, timed_page fixtures for Playwright metrics
  - terminal summary table printed after the run
  - JSON and CSV reports written to the working directory

The timed_page fixture wraps page.goto() so that navigation time is captured
automatically.  It also attaches Playwright event listeners for network
request/response pairs, console errors, and page errors.
"""

import time

import pytest
from playwright.sync_api import sync_playwright

from utils.timing_helper import (
    TimingCollector,
    print_terminal_summary,
    write_csv_report,
    write_json_report,
)

# Module-level collector shared across all hooks and fixtures
_collector = TimingCollector()


# ─── pytest lifecycle hooks ───────────────────────────────────────────────────

def pytest_runtest_logreport(report):
    """Record setup / call / teardown durations for every test."""
    metrics = _collector.get_or_create(report.nodeid)
    duration_ms = round(report.duration * 1000, 2)

    if report.when == "setup":
        metrics.setup_ms = duration_ms
    elif report.when == "call":
        metrics.call_ms = duration_ms
    elif report.when == "teardown":
        metrics.teardown_ms = duration_ms
        metrics.total_ms = round(
            metrics.setup_ms + metrics.call_ms + metrics.teardown_ms, 2
        )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print the timing summary table at the end of the test session."""
    print_terminal_summary(_collector.all_records())


def pytest_sessionfinish(session, exitstatus):
    """Write JSON and CSV timing reports at the end of the session."""
    records = _collector.all_records()
    if records:
        write_json_report(records, path="timing_report.json")
        write_csv_report(records, path="timing_report.csv")


# ─── Timed Playwright fixtures ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance():
    """Start a Playwright session (session-scoped)."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def timed_browser(playwright_instance):
    """
    Launch Chromium and record the launch time.

    Session-scoped so the browser is reused across all tests, matching the
    common pattern for faster test runs.  The launch duration is stored on the
    collector and copied to each test's metrics when a context is created.
    """
    t0 = time.monotonic()
    # headless=True is used here so the shared fixture works in CI without a
    # display server.  Change to headless=False for local debugging.
    browser = playwright_instance.chromium.launch(headless=True)
    _collector._browser_launch_ms = round((time.monotonic() - t0) * 1000, 2)

    yield browser
    browser.close()


@pytest.fixture(scope="function")
def timed_context(timed_browser, request):
    """
    Create a browser context and record creation and close times.

    Also copies the shared browser launch time into the per-test metrics so
    the full infrastructure cost is visible for each test.
    """
    test_name = request.node.nodeid
    metrics = _collector.get_or_create(test_name)
    metrics.browser_launch_ms = getattr(_collector, "_browser_launch_ms", 0.0)

    t0 = time.monotonic()
    context = timed_browser.new_context()
    metrics.context_create_ms = round((time.monotonic() - t0) * 1000, 2)

    yield context

    t0 = time.monotonic()
    context.close()
    metrics.context_close_ms = round((time.monotonic() - t0) * 1000, 2)


@pytest.fixture(scope="function")
def timed_page(timed_context, request):
    """
    Create a page, attach diagnostic listeners, and wrap page.goto().

    Captures:
      - page creation time
      - page.goto() navigation time (last call wins for multi-navigation tests)
      - all network request/response pairs with durations
      - browser console errors
      - uncaught page errors
      - page close time
    """
    test_name = request.node.nodeid
    metrics = _collector.get_or_create(test_name)

    t0 = time.monotonic()
    page = timed_context.new_page()
    metrics.page_create_ms = round((time.monotonic() - t0) * 1000, 2)

    # Attach listeners for network, console, and page error events
    _collector.attach_page_listeners(page, metrics)

    # Wrap page.goto() to capture navigation time
    _original_goto = page.goto

    def _timed_goto(url, **kwargs):
        _t0 = time.monotonic()
        response = _original_goto(url, **kwargs)
        metrics.page_goto_ms = round((time.monotonic() - _t0) * 1000, 2)
        return response

    page.goto = _timed_goto

    yield page

    t0 = time.monotonic()
    page.close()
    metrics.page_close_ms = round((time.monotonic() - t0) * 1000, 2)

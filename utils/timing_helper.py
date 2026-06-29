"""
utils/timing_helper.py

Reusable timing and metrics collection helper for Playwright pytest tests.

Captures:
  - pytest phase durations  (setup / call / teardown / total)
  - browser launch time
  - context create/close time
  - page create/close time
  - page.goto() navigation time
  - per-request/response network timings
  - console errors and page errors

Reporting helpers:
  - print_terminal_summary()  – human-readable table in the terminal
  - write_json_report()       – machine-readable JSON file
  - write_csv_report()        – spreadsheet-friendly CSV file
"""

import csv
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class NetworkRequest:
    """Timing and status for a single HTTP request/response pair."""
    url: str
    method: str
    status: Optional[int] = None
    duration_ms: float = 0.0


@dataclass
class TestMetrics:
    """All timing and diagnostic metrics collected for one test."""
    test_name: str

    # pytest phase durations
    setup_ms: float = 0.0
    call_ms: float = 0.0
    teardown_ms: float = 0.0
    total_ms: float = 0.0

    # Playwright infrastructure timings
    browser_launch_ms: float = 0.0
    context_create_ms: float = 0.0
    context_close_ms: float = 0.0
    page_create_ms: float = 0.0
    page_close_ms: float = 0.0

    # Navigation timing (last page.goto() call)
    page_goto_ms: float = 0.0

    # Network events
    network_requests: List[NetworkRequest] = field(default_factory=list)

    # Browser console / runtime errors
    console_errors: List[str] = field(default_factory=list)
    page_errors: List[str] = field(default_factory=list)


# ─── Collector ────────────────────────────────────────────────────────────────

class TimingCollector:
    """
    Central store for all per-test metrics.

    Usage in conftest.py
    --------------------
    _collector = TimingCollector()

    # Record pytest phase durations with pytest_runtest_logreport hook.
    # Use timed_browser / timed_context / timed_page fixtures for
    # Playwright-level timings.
    """

    def __init__(self):
        self._records: Dict[str, TestMetrics] = {}
        # Shared browser launch time (session-scoped browser is launched once)
        self._browser_launch_ms: float = 0.0

    def get_or_create(self, test_name: str) -> TestMetrics:
        if test_name not in self._records:
            self._records[test_name] = TestMetrics(test_name=test_name)
        return self._records[test_name]

    def all_records(self) -> List[TestMetrics]:
        return list(self._records.values())

    def attach_page_listeners(self, page, metrics: TestMetrics) -> None:
        """
        Attach Playwright event listeners to *page* so that network timings,
        console errors, and page errors are automatically recorded into *metrics*.

        Call this immediately after creating the page object.
        """
        _pending: Dict[str, float] = {}

        def on_request(request):
            _pending[request.url] = time.monotonic()

        def on_response(response):
            start = _pending.pop(response.url, None)
            duration_ms = round((time.monotonic() - start) * 1000, 2) if start is not None else 0.0
            metrics.network_requests.append(
                NetworkRequest(
                    url=response.url,
                    method=response.request.method,
                    status=response.status,
                    duration_ms=duration_ms,
                )
            )

        def on_console(msg):
            if msg.type == "error":
                metrics.console_errors.append(msg.text)

        def on_page_error(error):
            metrics.page_errors.append(str(error))

        page.on("request", on_request)
        page.on("response", on_response)
        page.on("console", on_console)
        page.on("pageerror", on_page_error)


# ─── Reporting helpers ────────────────────────────────────────────────────────

def print_terminal_summary(records: List[TestMetrics]) -> None:
    """Print a human-readable timing summary to the terminal after the test run."""
    if not records:
        return

    print("\n" + "=" * 60)
    print("Playwright Timing Summary")
    print("=" * 60)

    for rec in records:
        print(f"\n{rec.test_name}")
        print(f"  setup_ms:           {rec.setup_ms:.2f}")
        print(f"  call_ms:            {rec.call_ms:.2f}")
        print(f"  teardown_ms:        {rec.teardown_ms:.2f}")
        print(f"  total_ms:           {rec.total_ms:.2f}")
        if rec.browser_launch_ms:
            print(f"  browser_launch_ms:  {rec.browser_launch_ms:.2f}")
        if rec.context_create_ms:
            print(f"  context_create_ms:  {rec.context_create_ms:.2f}")
        if rec.page_create_ms:
            print(f"  page_create_ms:     {rec.page_create_ms:.2f}")
        if rec.page_goto_ms:
            print(f"  page_goto_ms:       {rec.page_goto_ms:.2f}")
        if rec.network_requests:
            print(f"  network_requests:   {len(rec.network_requests)}")
        if rec.console_errors:
            print(f"  console_errors:     {len(rec.console_errors)}")
            for err in rec.console_errors:
                print(f"    - {err}")
        if rec.page_errors:
            print(f"  page_errors:        {len(rec.page_errors)}")
            for err in rec.page_errors:
                print(f"    - {err}")

    print("=" * 60)


def write_json_report(records: List[TestMetrics], path: str = "timing_report.json") -> None:
    """Write all timing metrics to a JSON file for programmatic analysis."""
    data = {}
    for rec in records:
        data[rec.test_name] = {
            "setup_ms": rec.setup_ms,
            "call_ms": rec.call_ms,
            "teardown_ms": rec.teardown_ms,
            "total_ms": rec.total_ms,
            "browser_launch_ms": rec.browser_launch_ms,
            "context_create_ms": rec.context_create_ms,
            "context_close_ms": rec.context_close_ms,
            "page_create_ms": rec.page_create_ms,
            "page_close_ms": rec.page_close_ms,
            "page_goto_ms": rec.page_goto_ms,
            "network_requests": [
                {
                    "url": r.url,
                    "method": r.method,
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                }
                for r in rec.network_requests
            ],
            "console_errors": rec.console_errors,
            "page_errors": rec.page_errors,
        }
    Path(path).write_text(json.dumps(data, indent=2))
    print(f"\nJSON report written to: {path}")


def write_csv_report(records: List[TestMetrics], path: str = "timing_report.csv") -> None:
    """Write summary timing data to a CSV file for spreadsheet analysis."""
    if not records:
        return

    fieldnames = [
        "test_name",
        "setup_ms",
        "call_ms",
        "teardown_ms",
        "total_ms",
        "browser_launch_ms",
        "context_create_ms",
        "page_create_ms",
        "page_goto_ms",
        "network_request_count",
        "console_error_count",
        "page_error_count",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow({
                "test_name": rec.test_name,
                "setup_ms": rec.setup_ms,
                "call_ms": rec.call_ms,
                "teardown_ms": rec.teardown_ms,
                "total_ms": rec.total_ms,
                "browser_launch_ms": rec.browser_launch_ms,
                "context_create_ms": rec.context_create_ms,
                "page_create_ms": rec.page_create_ms,
                "page_goto_ms": rec.page_goto_ms,
                "network_request_count": len(rec.network_requests),
                "console_error_count": len(rec.console_errors),
                "page_error_count": len(rec.page_errors),
            })

    print(f"CSV report written to: {path}")

"""
test_timing_demo.py

Demonstration of the Playwright timing/metrics helper.

This test shows how the timed_page fixture from conftest.py automatically
collects and reports:
  - pytest phase durations (setup / call / teardown / total)
  - browser launch time
  - context creation and close time
  - page creation and close time
  - page.goto() navigation time
  - network request/response timings
  - console errors and page errors

After the test run, three outputs are produced automatically:
  1. A terminal summary table (printed by pytest_terminal_summary)
  2. timing_report.json  (written by pytest_sessionfinish)
  3. timing_report.csv   (written by pytest_sessionfinish)

Run with:
    pytest test_timing_demo.py -v -s
"""

import pytest


def test_homepage_timing(timed_page):
    """
    Navigate to example.com and verify the page loads correctly.

    The timed_page fixture records all timing metrics automatically.
    No extra code is needed in the test itself.
    """
    timed_page.goto("https://example.com")
    assert "Example Domain" in timed_page.title()


def test_two_navigations(timed_page):
    """
    Navigate twice to show that page_goto_ms captures the last navigation.

    Network timings include requests from both navigations.
    """
    timed_page.goto("https://example.com")
    assert timed_page.title() != ""

    timed_page.goto("https://example.com/")
    assert timed_page.title() != ""


def test_console_and_network(timed_page):
    """
    Load a page and inspect the collected network and console metrics.

    After the test, metrics are visible in the terminal summary and reports.
    """
    timed_page.goto("https://example.com")

    title = timed_page.title()
    assert title != "", "Page title should not be empty"

    # Example: manually check that at least one network request was recorded.
    # In a real test you would assert on specific API endpoints.
    # The full list is available in timing_report.json after the run.


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

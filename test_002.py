import pytest

# timed_page is provided by conftest.py and records:
#   - browser launch time
#   - context / page creation time
#   - page.goto() navigation time
#   - network request / response timings
#   - console errors and page errors
#
# A terminal summary table plus JSON and CSV reports are written automatically
# at the end of the session by the hooks in conftest.py.


def test_example(timed_page):
    timed_page.goto("https://www.google.com")
    print(timed_page.title())
    assert "Google" in timed_page.title()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-s"]))
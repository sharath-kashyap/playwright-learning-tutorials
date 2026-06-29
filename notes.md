# Playwright Notes

## Playwright architecture
Playwright uses a layered automation model where user test scripts interact with the Playwright core, which controls real browser engines like Chromium, Firefox, and WebKit through isolated browser contexts and pages.

### Main parts
- **Test code**: Written in JavaScript/TypeScript, Python, Java, or .NET using Playwright APIs.
- **Playwright core/driver**: Receives commands, manages sessions, applies auto-waiting, and communicates with browsers.
- **Browser instance**: A real browser process such as Chromium, Firefox, or WebKit.
- **Browser context**: An isolated browser session, similar to an incognito profile.
- **Page**: A single tab inside a browser context.

### Execution flow
1. Launch browser
2. Create browser context
3. Open page
4. Execute test steps
5. Auto-wait for actions/assertions
6. Collect artifacts if configured
7. Close page/context/browser

## Playwright lifecycle example in Python
```python
from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://example.com")
            print(page.title())
        finally:
            page.close()
            context.close()
            browser.close()

run_test()
```

## Playwright fixtures in Python
### Built-in fixture example
```python
def test_homepage(page):
    page.goto("https://example.com")
    assert "Example" in page.title()
```

### Custom fixture example
```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def page_fixture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        yield page

        page.close()
        context.close()
        browser.close()
```

### Recommended scoped fixtures
```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()
```

## Browser, context, and page
### Browser
Represents the launched browser process.

**Common methods/properties**
- `new_context()`
- `contexts`
- `close()`
- `browser_type`
- `is_connected()`
- `version`

### Context
Represents an isolated browser session.

**Common methods/properties**
- `new_page()`
- `pages`
- `close()`
- `cookies()`
- `add_cookies()`
- `clear_cookies()`
- `storage_state()`
- `grant_permissions()`
- `set_default_timeout()`
- `route()`

### Page
Represents a browser tab.

**Common methods/properties**
- `goto()`
- `click()`
- `fill()`
- `locator()`
- `get_by_role()`
- `title()`
- `url`
- `content()`
- `screenshot()`
- `reload()`
- `go_back()` / `go_forward()`
- `wait_for_url()`
- `wait_for_load_state()`
- `route()`
- `close()`

## Scaling and performance in Playwright
Playwright scales mainly through **parallel workers**, **browser reuse**, **isolated browser contexts**, and **CI distribution**.

### How scaling works
- **Parallel workers**: Tests run in separate worker processes.
- **Context isolation**: Fresh contexts provide test isolation without the cost of relaunching the browser.
- **Projects**: Running across multiple browsers/devices increases coverage but multiplies execution time.
- **Sharding**: Large suites can be split across multiple CI machines.

### What improves performance
- Reusing authentication with storage state
- Using API-based setup instead of repeated UI flows
- Keeping tests independent for safe parallelism
- Limiting screenshots, videos, and traces to failures or retries
- Using stable locators and avoiding unnecessary waits

### What hurts performance
- `wait_for_timeout()`
- Repeated UI login in every test
- Shared mutable data between tests
- Giant end-to-end flows
- Excessive artifact capture for passing tests
- Relaunching browsers too often

### Scaled execution flow
1. CI starts multiple workers
2. Each worker launches a browser
3. Each test gets a fresh context
4. Test runs in isolation
5. Context closes after the test
6. Results are merged into reports

### Interview summary
Playwright scales through worker-based parallelism and context isolation. Performance improves with browser reuse, storage state, API-driven setup, and CI sharding. Most slowdowns come from poor test design, shared state, excessive artifacts, or environment bottlenecks.

# Playwright Notes

This repository contains Playwright learning notes.

## Topics
- Architecture
- Browser, Context, Page
- Fixtures
- Locators
- Waits and Assertions
- Network Interception
- Authentication
- Debugging
- CI/CD
- Scaling and Performance

## Playwright Architecture

Playwright follows a layered browser automation architecture where user test code communicates with the Playwright API, and Playwright in turn controls real browser engines such as Chromium, Firefox, and WebKit.

### Architecture Flow
- Test code
- Playwright client/library
- Browser instance
- Browser context
- Page
- Web application DOM

### Simple Execution Flow
1. Playwright starts the browser.
2. A browser context is created for isolation.
3. A page is opened inside the context.
4. Test actions are performed on the page.
5. Assertions are executed.
6. Page, context, and browser are closed after execution.

### Why the Architecture is Powerful
- Provides real browser automation instead of DOM simulation
- Supports cross-browser testing with a single API
- Uses isolated browser contexts for clean test separation
- Includes auto-waiting for more reliable test execution
- Supports multiple pages and contexts in the same test

## Browser, Context, and Page

Playwright uses three important objects in a hierarchy:

- Browser
- Browser Context
- Page

### 1. Browser
A browser represents the full browser process launched by Playwright.

#### Responsibilities
- Launches and manages the browser instance
- Owns one or more browser contexts
- Provides access to browser-level operations

#### Common Methods and Properties
- `browser.new_context()` - creates a new isolated browser context
- `browser.contexts` - returns available contexts
- `browser.close()` - closes the browser
- `browser.is_connected()` - checks if browser is still connected
- `browser.version` - gives browser version

### 2. Browser Context
A browser context is an isolated session inside the browser. It works like an incognito profile.

#### Responsibilities
- Maintains isolated cookies and storage
- Separates authentication/session data between tests
- Owns one or more pages
- Helps enable parallel and independent execution

#### Common Methods and Properties
- `context.new_page()` - creates a new tab/page
- `context.pages` - returns pages in the context
- `context.close()` - closes the context
- `context.cookies()` - returns cookies
- `context.add_cookies()` - adds cookies
- `context.clear_cookies()` - clears cookies
- `context.storage_state()` - captures storage and cookies
- `context.route()` - intercepts network requests
- `context.grant_permissions()` - grants browser permissions

### 3. Page
A page represents a single browser tab inside a context.

#### Responsibilities
- Interacts with application UI
- Navigates to URLs
- Performs actions like click, fill, type, hover
- Executes validations and assertions
- Supports screenshots, downloads, dialogs, and frames

#### Common Methods and Properties
- `page.goto()` - navigates to a URL
- `page.click()` - clicks an element
- `page.fill()` - fills an input field
- `page.locator()` - creates a locator
- `page.get_by_role()` - recommended user-facing locator strategy
- `page.title()` - gets page title
- `page.url` - gets current URL
- `page.screenshot()` - captures screenshot
- `page.wait_for_url()` - waits for navigation
- `page.wait_for_load_state()` - waits for page loading states
- `page.close()` - closes the tab/page

## Hierarchy Summary
- Browser contains one or more contexts
- Context contains one or more pages
- Page interacts with the actual web content

### Easy Analogy
- Browser = Chrome application
- Context = Incognito window/profile
- Page = Individual browser tab

## Python Example

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://example.com")
    print(page.title())

    page.close()
    context.close()
    browser.close()
```

### What Happens in the Example
- `browser` launches the real browser
- `context` creates an isolated session
- `page` opens a new tab
- actions are executed on the page
- cleanup closes page, context, and browser

## Playwright Fixtures in Python

Fixtures help manage setup and teardown cleanly in pytest-based Playwright frameworks.

### Built-in Fixture Example
```python
def test_homepage(page):
    page.goto("https://example.com")
    assert "Example" in page.title()
```

### Custom Fixture Example
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

### Recommended Scoped Fixtures
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

### Fixture Notes
- Code before `yield` is setup
- Code after `yield` is teardown
- Common scopes are `function`, `class`, `module`, and `session`
- A good practice is browser at `session` scope and context/page at `function` scope

## Scaling and Performance in Playwright

Playwright scales mainly through worker-based parallelism, browser reuse, isolated browser contexts, and CI distribution.

### How Scaling Works
- **Parallel workers**: Test files run in separate worker processes
- **Context isolation**: Fresh contexts isolate tests without paying the cost of relaunching the browser every time
- **Projects**: Multi-browser and multi-device runs improve coverage but increase total execution count
- **Sharding**: Large suites can be split across multiple CI machines

### What Improves Performance
- Reusing login/authentication with storage state
- Using API-based setup instead of repeated UI setup flows
- Keeping tests independent for safe parallelism
- Limiting screenshots, videos, and traces to failures or retries
- Using stable locators and avoiding unnecessary waits
- Minimizing full browser relaunches

### What Hurts Performance
- `wait_for_timeout()`
- Repeated UI login in every test
- Shared mutable test data between tests
- Very long end-to-end flows for simple validations
- Excessive artifact capture for all passing tests
- Relaunching browsers too frequently

### Scaled Execution Flow
1. CI starts multiple workers
2. Each worker launches or connects to a browser
3. Each test gets a fresh browser context
4. Test runs in isolation
5. Context closes after the test
6. Results are merged into reports

### Performance Tuning Mindset
When a suite is slow, review these layers:
- test design
- framework configuration
- CI machine capacity
- backend or environment bottlenecks
- application rendering and loading behavior

### Interview Summary
Playwright scales through parallel workers and isolated browser contexts. Performance improves through browser reuse, storage state, API-driven setup, and CI sharding. Most slowdowns usually come from poor test design, shared state, excessive artifacts, or infrastructure bottlenecks.

## Playwright vs Selenium Architecture

Architecturally, Playwright is more modern, tightly integrated, and isolation-first, while Selenium is more protocol-driven, distributed, and browser-driver based.

### High-Level Difference

#### Playwright
- Test code talks to the Playwright library
- Playwright directly manages browser automation through its own integration layer
- Uses browser contexts as lightweight isolated sessions
- Has built-in auto-waiting, tracing, network interception, and multi-tab/session control

#### Selenium
- Test code talks to WebDriver client bindings
- Commands go through the WebDriver protocol
- A separate browser driver is usually involved, such as ChromeDriver, GeckoDriver, or EdgeDriver
- Browser isolation is usually done with separate browser sessions, which are heavier than Playwright contexts

### Communication Model

#### Playwright
Flow:
- Test Code
- Playwright API
- Browser Engine

Playwright has a more direct automation model and tighter control over the browser.

#### Selenium
Flow:
- Test Code
- Selenium Client
- WebDriver Protocol
- Browser Driver
- Browser

There are more layers involved in Selenium execution.

### Browser Driver Dependency

#### Playwright
- No traditional separate driver management
- Browsers are bundled or managed by Playwright tooling
- Less setup friction

#### Selenium
- Typically depends on browser-specific drivers
- Version compatibility between browser and driver matters
- Usually has more setup and maintenance overhead

### Session Isolation Model

#### Playwright
- One browser can create many contexts
- One context can create many pages
- Contexts are lightweight and isolated
- Cookies, storage, and sessions are separated per context

#### Selenium
- Isolation is usually one WebDriver session per browser instance
- New sessions are heavier compared to Playwright contexts

### Waiting Model

#### Playwright
- Built-in auto-waiting is part of the architecture
- Checks visibility, stability, enabled state, and event readiness before actions

#### Selenium
- Usually relies more on implicit waits, explicit waits, and fluent waits
- Often requires additional manual wait logic

### Network and Modern Web Testing

#### Playwright
- Built-in support for request interception
- Response mocking
- API testing
- Tracing, screenshots, and videos

#### Selenium
- Some capabilities require external tools or extra integrations
- Historically less built-in support for modern network control

### Execution Model

#### Playwright
- Built with modern parallel execution in mind
- Lightweight isolation using contexts
- Built-in test runner and debugging capabilities

#### Selenium
- Commonly combined with external tools such as TestNG, JUnit, pytest, NUnit, or Selenium Grid
- More flexible, but often requires more assembly

### Quick Comparison Table

| Aspect | Playwright | Selenium |
|---|---|---|
| Communication | Direct Playwright automation layer | WebDriver protocol |
| Driver dependency | No traditional separate driver management | Uses browser drivers |
| Isolation | Browser contexts | Separate WebDriver sessions |
| Waiting | Built-in auto-waiting | Mostly explicit or implicit waits |
| Network mocking | Built-in | More limited or needs extra setup |
| Tooling | Integrated | Ecosystem-based |
| Parallel testing | Lightweight and efficient | Heavier session model |

### Summary
Playwright is designed as a modern automation framework with direct browser control, lightweight isolation, and many built-in testing features. Selenium is built around the WebDriver standard and provides broad ecosystem support, but usually requires more setup and manual control.

## Update Process
This file will be updated incrementally with additional Playwright details over time.

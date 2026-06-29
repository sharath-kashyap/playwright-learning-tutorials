# Playwright Interview Prep Notes

A polished interview-prep guide for Playwright with concise explanations, practical examples, and ready-to-say answers.

## Table of Contents
- 1. Quick Interview Summary
- 2. Playwright Architecture
- 3. Browser vs Context vs Page
- 4. Playwright Lifecycle in Python
- 5. Fixtures in Python
- 6. Reusing Login Across Multiple Tests
- 7. Repo-Ready Folder Structure
- 8. Scaling and Performance
- 9. Playwright vs Selenium
- 10. Rapid-Fire Interview Questions
- 11. Strong Answer Patterns

## 1. Quick Interview Summary

If an interviewer asks, "What should I know about Playwright?", a strong concise answer is:

- Playwright is a modern browser automation framework
- It supports Chromium, Firefox, and WebKit with a single API
- It uses browser contexts for lightweight isolation
- It includes auto-waiting, tracing, network interception, and parallel execution
- It is well-suited for reliable end-to-end and UI automation

## 2. Playwright Architecture

### Interview Answer
Playwright follows a layered automation architecture where test code talks to the Playwright API, and Playwright controls real browser engines such as Chromium, Firefox, and WebKit.

### Architecture Flow
- Test code
- Playwright client/library
- Browser instance
- Browser context
- Page
- Web application DOM

### Execution Flow
1. Playwright launches the browser
2. A browser context is created for isolation
3. A page is opened inside the context
4. Test actions are performed on the page
5. Assertions are executed
6. Page, context, and browser are closed after execution

### Why This Architecture Is Strong
- Real browser automation instead of DOM simulation
- Cross-browser support with one API
- Context-based isolation for clean tests
- Built-in auto-waiting for better stability
- Support for multiple pages and contexts in the same test

### One-Line Version
Playwright uses a layered client-to-browser architecture with isolated browser contexts and pages, which makes automation reliable, fast, and cross-browser.

## 3. Browser vs Context vs Page

This is one of the most common interview topics.

### Browser
A browser is the full browser process launched by Playwright.

**Responsibilities**
- Launches and manages the browser instance
- Owns one or more browser contexts
- Provides browser-level operations

**Common methods/properties**
- `browser.new_context()`
- `browser.contexts`
- `browser.close()`
- `browser.is_connected()`
- `browser.version`

### Browser Context
A browser context is an isolated session inside the browser, similar to an incognito profile.

**Responsibilities**
- Maintains isolated cookies and storage
- Separates authentication/session data between tests
- Owns one or more pages
- Enables parallel and independent execution

**Common methods/properties**
- `context.new_page()`
- `context.pages`
- `context.close()`
- `context.cookies()`
- `context.add_cookies()`
- `context.clear_cookies()`
- `context.storage_state()`
- `context.route()`
- `context.grant_permissions()`

### Page
A page is a single browser tab inside a context.

**Responsibilities**
- Interacts with the application UI
- Navigates to URLs
- Performs actions such as click, fill, type, and hover
- Executes validations and assertions
- Supports screenshots, downloads, dialogs, and frames

**Common methods/properties**
- `page.goto()`
- `page.click()`
- `page.fill()`
- `page.locator()`
- `page.get_by_role()`
- `page.title()`
- `page.url`
- `page.screenshot()`
- `page.wait_for_url()`
- `page.wait_for_load_state()`
- `page.close()`

### Hierarchy Summary
- Browser contains one or more contexts
- Context contains one or more pages
- Page interacts with the actual web content

### Easy Analogy
- Browser = Chrome application
- Context = Incognito window/profile
- Page = Individual browser tab

### Ready-to-Say Answer
Browser is the top-level browser process, context is an isolated session within that browser, and page is a tab inside the context where actual UI actions happen.

## 4. Playwright Lifecycle in Python

### Simple Python Example
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

### What Happens Here
- `sync_playwright()` starts Playwright
- `browser` launches the real browser
- `context` creates an isolated session
- `page` opens a new tab
- actions are executed on the page
- cleanup closes page, context, and browser

### Interview Explanation
Initialization usually starts with `sync_playwright()` or `async_playwright()`, then the browser is launched, a context is created, and a page is opened. After test completion, page, context, and browser are closed to release resources and keep runs isolated.

## 5. Fixtures in Python

Fixtures are used to manage setup and teardown cleanly in pytest-based Playwright frameworks.

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

### How test cases get the `page` instance
This is the key idea in pytest fixtures.

When a test is written like this:

```python
def test_dashboard(page):
    page.goto("https://app.example.com/dashboard")
```

pytest sees that the test needs a fixture named `page`. It looks for the `page` fixture definition, runs it, and injects the yielded object into the test function.

That means this fixture:

```python
@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()
```

creates the Playwright page object and passes it into the test automatically.

Flow:
1. pytest starts the test
2. pytest sees `page` in the test arguments
3. pytest resolves the dependency on `context`
4. the `context` fixture creates a browser context
5. the `page` fixture creates `context.new_page()`
6. pytest injects that page object into the test
7. after the test, teardown runs in reverse order

### Fixture Notes
- Code before `yield` is setup
- Code after `yield` is teardown
- Common scopes are `function`, `class`, `module`, and `session`
- Good practice: browser at `session` scope and context/page at `function` scope

### Ready-to-Say Answer
In Playwright Python with pytest, fixtures help manage browser, context, and page setup and teardown. They improve reusability, readability, and test isolation.

## 6. Reusing Login Across Multiple Tests

### Goal
Avoid logging in through the UI in every test. Login once, save the authenticated browser state, and reuse it in all tests.

### Framework-Level Idea
- create auth state once
- save cookies and local storage into a file
- create a new context per test using that saved auth state
- create a new page from that context

### Storage State Details
`context.storage_state()` returns a JSON snapshot of the browser context's authenticated state. It typically includes:
- cookies
- localStorage entries grouped by origin

### Example Storage State JSON
```json
{
  "cookies": [
    {
      "name": "sessionid",
      "value": "7f3a9c2d4b1e8a90",
      "domain": "app.example.com",
      "path": "/",
      "expires": 1760000000,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    },
    {
      "name": "csrf_token",
      "value": "b8c1f4e2a7",
      "domain": "app.example.com",
      "path": "/",
      "expires": -1,
      "httpOnly": false,
      "secure": true,
      "sameSite": "Strict"
    }
  ],
  "origins": [
    {
      "origin": "https://app.example.com",
      "localStorage": [
        {
          "name": "authToken",
          "value": "eyJhbGciOi..."
        },
        {
          "name": "theme",
          "value": "dark"
        }
      ]
    }
  ]
}
```

### What this means
- `cookies` stores session/auth cookies and other browser cookies
- `origins` stores localStorage values for each origin
- This file can be reused later with:

```python
browser.new_context(storage_state="user.json")
```

### Repo-Ready Example

#### `config/settings.py`
```python
BASE_URL = "https://app.example.com"
AUTH_STATE_DIR = "playwright_framework/.auth"
USERNAME = "testuser"
PASSWORD = "secret123"
```

#### `pages/login_page.py`
```python
class LoginPage:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(f"{base_url}/login")

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("button[type='submit']")

    def wait_for_login_success(self):
        self.page.wait_for_url("**/dashboard")
```

#### `utils/auth_manager.py`
```python
from pathlib import Path
from playwright.sync_api import sync_playwright
from config.settings import BASE_URL, AUTH_STATE_DIR, USERNAME, PASSWORD
from pages.login_page import LoginPage

AUTH_FILE = Path(AUTH_STATE_DIR) / "user.json"


def create_auth_state():
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login_page = LoginPage(page)
        login_page.open(BASE_URL)
        login_page.login(USERNAME, PASSWORD)
        login_page.wait_for_login_success()

        context.storage_state(path=str(AUTH_FILE))
        browser.close()


def ensure_auth_state():
    if not AUTH_FILE.exists():
        create_auth_state()

    return str(AUTH_FILE)
```

#### `conftest.py`
```python
import pytest
from playwright.sync_api import sync_playwright
from utils.auth_manager import ensure_auth_state


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="session", autouse=True)
def setup_auth_state():
    ensure_auth_state()


@pytest.fixture(scope="function")
def context(browser):
    auth_file = ensure_auth_state()
    context = browser.new_context(storage_state=auth_file)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()
```

#### `tests/test_dashboard.py`
```python
from config.settings import BASE_URL


def test_dashboard_header(page):
    page.goto(f"{BASE_URL}/dashboard")
    assert page.locator("h1").is_visible()


def test_recent_activity_widget(page):
    page.goto(f"{BASE_URL}/dashboard")
    assert page.locator("#recent-activity").is_visible()
```

#### `tests/test_profile.py`
```python
from config.settings import BASE_URL


def test_profile_page(page):
    page.goto(f"{BASE_URL}/profile")
    assert page.locator("text=Profile").is_visible()


def test_edit_profile_button(page):
    page.goto(f"{BASE_URL}/profile")
    assert page.locator("button:has-text('Edit')").is_visible()
```

### How the page is available in logged-in tests
The page still comes from the `page` fixture. The only difference is that the `context` fixture now uses:

```python
browser.new_context(storage_state=auth_file)
```

So the flow becomes:
1. ensure auth file exists
2. create a browser context with saved login state
3. create a page from that context
4. inject that page into the test

The test still just asks for `page`:

```python
def test_profile_page(page):
    page.goto("https://app.example.com/profile")
```

but that page is now already authenticated because its context was created from the saved storage state.

### Why this pattern works well
- login UI runs once instead of for every test
- tests remain isolated because each test gets a fresh context
- execution becomes faster and more stable
- framework stays clean and reusable

### Ready-to-Say Answer
To avoid repeated logins, I create storage state once, then every test gets a fresh browser context initialized with that saved state. The `page` object is still provided by a fixture, but it comes from an authenticated context, so tests stay isolated and faster.

## 7. Repo-Ready Folder Structure

```text
playwright_framework/
│
├── .auth/
│   └── user.json
│
├── config/
│   └── settings.py
│
├── pages/
│   └── login_page.py
│
├── tests/
│   ├── test_dashboard.py
│   └── test_profile.py
│
├── utils/
│   └── auth_manager.py
│
└── conftest.py
```

### Optional expansion for larger frameworks
```text
playwright_framework/
│
├── .auth/
├── config/
│   ├── settings.py
│   └── environments.py
│
├── pages/
│   ├── login_page.py
│   ├── dashboard_page.py
│   └── profile_page.py
│
├── fixtures/
│   └── browser_fixtures.py
│
├── test_data/
│   └── users.py
│
├── utils/
│   ├── auth_manager.py
│   └── helpers.py
│
├── tests/
│   ├── smoke/
│   ├── regression/
│   └── api/
│
└── conftest.py
```

## 8. Scaling and Performance

### Interview Answer
Playwright scales through worker-based parallelism, isolated browser contexts, browser reuse, and CI sharding.

### Short Interview Version
Playwright scales best when tests are isolated, browser contexts are created per test, and authentication state is reused instead of logging in through the UI every time. For large suites, I run tests in parallel, shard them across CI workers, and keep artifacts like traces and videos focused on failures to reduce overhead.

### How Scaling Works
- **Parallel workers**: Test files run in separate worker processes
- **Context isolation**: Fresh contexts isolate tests without relaunching the browser every time
- **Projects**: Multi-browser and multi-device runs increase coverage but also increase total execution count
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

### Performance Tuning Checklist
- Is login reused?
- Is setup done through API where possible?
- Are tests independent?
- Are workers configured correctly?
- Are traces/videos limited to failures?
- Is the environment the real bottleneck?

### Pytest-xdist Example
```bash
pip install pytest-xdist
pytest -n auto
```

### Visual Worker Distribution Example
```text
Tests:        test_a   test_b   test_c   test_d   test_e   test_f

Worker 1:     test_a ------------------------> test_d
Worker 2:     test_b ---------> test_e
Worker 3:     test_c ----------> test_f
```

### How to read this
- pytest-xdist creates multiple worker processes
- workers pick up tests as they become available
- faster workers can grab more tests
- the split is usually load-balanced, not fixed
- exact assignment can change run to run

### Configuring Multiple pytest Options
Pytest supports multiple options at the same time, and they can be configured in a few different places depending on whether you want defaults or temporary overrides.

#### 1. `pytest.ini`
Use this for project-wide defaults.

```ini
[pytest]
addopts = -n auto -v --tb=short --maxfail=2
testpaths = tests
python_files = test_*.py
markers =
    smoke: smoke tests
    regression: regression tests
```

#### 2. `pyproject.toml`
If the project uses `pyproject.toml`, pytest options can also be configured there.

```toml
[tool.pytest.ini_options]
addopts = "-n auto -v --tb=short --maxfail=2"
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = [
  "smoke: smoke tests",
  "regression: regression tests",
]
```

#### 3. Command-line arguments
For one-off runs, pass options directly when running pytest.

```bash
pytest tests -n 4 -v --tb=short --maxfail=2 -m smoke
```

#### Example Breakdown
- `-n 4` runs tests across 4 workers
- `-v` enables verbose output
- `--tb=short` shortens traceback output
- `--maxfail=2` stops after 2 failures
- `-m smoke` runs only tests marked as smoke

#### Ready-to-Say Answer
Pytest options can be configured in `pytest.ini`, `pyproject.toml`, or directly on the command line. I usually keep shared defaults in a config file and use command-line arguments for temporary overrides.

### Playwright + pytest-xdist Example `conftest.py`
```python
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=True)
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

### Ready-to-Say Answer
Playwright performance improves when you reuse browser state smartly, keep tests independent, use parallel workers, and avoid unnecessary UI setup and hard waits.

## 9. Playwright vs Selenium

### Interview Answer
Playwright is more modern, isolation-first, and tightly integrated, while Selenium is WebDriver-based and more ecosystem-driven.

### High-Level Difference

#### Playwright
- Test code talks to the Playwright library
- Playwright directly manages browser automation through its own integration layer
- Uses browser contexts as lightweight isolated sessions
- Includes built-in auto-waiting, tracing, network interception, and multi-tab/session control

#### Selenium
- Test code talks to WebDriver client bindings
- Commands go through the WebDriver protocol
- Usually depends on a separate browser driver such as ChromeDriver or GeckoDriver
- Browser isolation is usually heavier than Playwright contexts

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

### Ready-to-Say Answer
Playwright gives faster setup, lightweight isolation, and more built-in testing features, while Selenium offers broader historical ecosystem support and standard WebDriver-based automation.

## 10. Rapid-Fire Interview Questions

### Architecture
1. What is Playwright architecture?
2. How does Playwright communicate with browsers?
3. Why are browser contexts important?
4. Why is Playwright considered more modern than older UI automation tools?

### Browser, Context, Page
5. What is the difference between browser, context, and page?
6. Why is context preferred for isolation?
7. Can one browser have multiple contexts?
8. Can one context have multiple pages?

### Fixtures
9. What is a fixture in pytest?
10. What does `yield` do in a fixture?
11. Why keep page and context at function scope?
12. How does pytest inject the `page` object into the test?

### Performance
13. How does Playwright support parallel execution?
14. What is sharding?
15. What slows down Playwright suites the most?
16. Why is `wait_for_timeout()` discouraged?
17. How do you avoid repeated login in Playwright?

### Comparison
18. What is the main difference between Playwright and Selenium?
19. Why is Playwright isolation lighter than Selenium?
20. What built-in features make Playwright attractive?
21. When might teams still use Selenium?

## 11. Strong Answer Patterns

Use these patterns in interviews:

### Pattern 1: Definition + Why It Matters
Example:
"A browser context is an isolated session inside the browser, and it matters because it keeps cookies, storage, and authentication separate between tests."

### Pattern 2: Concept + Practical Use
Example:
"Fixtures manage setup and teardown, which helps reduce duplicate code and improves test maintainability."

### Pattern 3: Comparison + Conclusion
Example:
"Playwright uses lightweight contexts for isolation, while Selenium typically uses heavier browser sessions, so Playwright usually scales parallel UI tests more efficiently."

## Final Revision Tip
If you are preparing for interviews, practice answering every topic in three forms:
- **one-line answer**
- **short explanation**
- **real project example**

That makes you sound both clear and experienced.

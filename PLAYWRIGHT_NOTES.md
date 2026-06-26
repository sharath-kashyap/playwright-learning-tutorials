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

## Update Process
This file will be updated incrementally with additional Playwright details over time.

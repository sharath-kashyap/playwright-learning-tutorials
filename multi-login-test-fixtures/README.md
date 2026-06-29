# Multi Login Test Fixtures

This folder contains a sample Playwright + pytest framework for multi-role login reuse.

## Roles
- admin
- user
- manager

## Included files
- `config/settings.py`
- `pages/login_page.py`
- `utils/auth_manager.py`
- `conftest.py`
- `tests/test_admin_access.py`
- `tests/test_multi_role_workflow.py`

## How it works
- Each role has its own credentials
- Authentication state is saved per role
- Each test gets a fresh browser context
- Each role fixture provides a separate authenticated page

## Example fixtures
- `admin_page`
- `user_page`
- `manager_page`

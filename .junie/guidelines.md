# FilamentColors Engineering Guidelines

This document captures practical guidelines derived from the current codebase. It should help you write code that fits the repository and run tests confidently.

Last updated: 2025-09-15 23:54 (local time)


## 1) Coding conventions used in this codebase

### Python
- Versions: Python >= 3.10, < 3.13 (see `pyproject.toml`).
- Formatting: Black and isort are used for consistent style.
  - Run formatter locally: `make pretty` (runs `black .` and `isort .`).
  - Import ordering follows isort defaults (see `pyproject.toml` dev dependencies for tooling).
- Linting: A dedicated linter is not configured; rely on Black/isort and tests.
- Type hints: Not enforced across the repo; add where they help readability.
- Naming:
  - Modules/files follow Django conventions (`models.py`, `views.py`, `urls.py`, etc.).
  - Tests use `test_*.py` naming.
- Django conventions:
  - Settings are split by environment (`filamentcolors/settings/{base,testing,prod,local}.py`).
  - Templates are organized under `filamentcolors/templates` with subfolders like `partials/` and `modals/`.
  - Static assets are in `filamentcolors/appstatic`. Do not use `filamentcolors.static`; it is for compiled assets only.
  - Reusable helpers live in `filamentcolors/helpers.py`, `filamentcolors/constants.py`, and similar small modules.
- Error handling & side effects:
  - Tests run with `POST_TO_SOCIAL_MEDIA = False` (see `settings/testing.py`) to avoid external side effects.

### JavaScript & Frontend
- Stack: Vanilla JS + jQuery + HTMX; no TypeScript.
- Style:
  - ES6 features are used (classes, arrow functions, `const`/`let`).
  - Semicolons are generally omitted; follow existing file style when editing nearby code.
  - Prefer progressive enhancement; HTMX lifecycle hooks (`htmx.onLoad`, etc.) appear in components like `appstatic/js/multiselect.js`.
  - Use `window` for storing global variables.
  - Prefer creating or updating web components where possible.
- Organization:
  - JS lives under `filamentcolors/appstatic/js/` with subfolders like `components/`.
  - CSS lives under `filamentcolors/appstatic/css/` (e.g., `main.css`).
  - Shared HTML snippets are in `filamentcolors/templates/partials/` and `filamentcolors/templates/modals/`.

### Commit scope
- Keep changes small and focused; prefer minimal diffs consistent with existing patterns.


## 2) Code organization and package structure

Top-level (selected):
- `filamentcolors/` — primary Django app/package
  - `settings/` — environment-specific Django settings
    - `base.py` — base settings imported by others
    - `testing.py` — imports base; sets `ENVIRONMENT = "testing"`, disables social posting
    - `prod.py`, `local.py` — other environment variants
  - `models.py` — core models
  - `views.py`, `staff_views.py`, `altcha_views.py` — view functions/views for site features
  - `urls.py` — app URL routes
  - `api/` — REST API endpoints (DRF is in dependencies)
  - `templates/` — Django templates
    - `partials/`, `modals/`, `standalone/`, etc.
  - `static/` — collected/static files (including vendor/admin) (DO NOT USE)
  - `appstatic/` — JS/CSS and assets
    - `js/` (e.g., `multiselect.js`, `components/card.js`)
    - `css/` (e.g., `main.css`)
  - `templatetags/` — custom Django template tags
  - `management/` — management commands (e.g., data import used by tests)
  - `tests/` — test suite (pytest)
    - `conftest.py`, multiple `test_*.py` modules (e.g., swatch, library, collections, inventory)
  - Supporting modules: `helpers.py`, `constants.py`, `middleware.py`, `sitemaps.py`, `social_media.py`, `colors.py`, etc.
- Tooling/infra:
  - `pyproject.toml` — Poetry project + pytest config and dev tools
  - `Makefile` — convenience targets for tests, runserver, formatting


## 3) Unit and integration testing approaches

### Test runner and configuration
- Test framework: pytest + pytest-django (see `pyproject.toml` dev dependencies).
- Settings for test runs are configured in `pyproject.toml` under `[tool.pytest.ini_options]`:
  - `DJANGO_SETTINGS_MODULE = "filamentcolors.settings.testing"`
  - `python_files = ["test_*.py", "*_test.py", "testing/python/*.py"]`
  - `testpaths = ["tests"]` (tests live in `filamentcolors/tests/`)
  - `addopts = "--cov --cov-report html"` for coverage reporting
- Coverage configuration omits migrations, management, tests, and specific large/3rd-party-like files (see `[tool.coverage.run]`).

### Database and fixtures
- `filamentcolors/tests/conftest.py`:
  - Seeds reference data once per test session via a management command (`import_pantone_ral.Command().handle()`), ensuring color data exists for tests.
  - Enables database access for all tests with an autouse fixture (`db`).
- As a result, you typically do not need to add `@pytest.mark.django_db` on each test — DB is available by default.

### Unit vs. integration tests
- Unit tests:
  - Focus on pure functions or small Django units (model methods, helpers) without external side effects.
  - Keep setup lightweight; when possible, construct objects directly or with simple factories/fixtures.
- Integration tests:
  - Use Django’s test client (pytest’s `client` or `async_client`) to hit views and endpoints.
  - Validate rendered templates, response codes, and behavior across layers (views, templates, DB).
  - External integrations (e.g., social posting) are disabled in testing settings; mock external calls as needed.

### How to run tests
- Full suite with coverage: `make tests` (equivalent to `poetry run pytest --cov --cov-report html`).
- Run a subset:
  - By node id: `poetry run pytest filamentcolors/tests/test_library.py::test_some_behavior`
  - By keyword: `poetry run pytest -k "swatch and not slow"`
- Parallel (optional): if desired, `pytest -n auto` with `pytest-xdist` (already in dev dependencies).
- Coverage HTML output goes to `htmlcov/` — open `htmlcov/index.html` after a run.

### Writing new tests
- Place new tests under `filamentcolors/tests/` using `test_*.py` naming.
- Use pytest style (functions or classes without `unittest.TestCase`).
- Database is enabled by default; use fixtures for data setup.
- Prefer assertions on business behavior and rendered output over implementation details.
- Always generate testing data or mock external calls. Never hard-code test data.

### Notes specific to this repo
- HTMX-driven interactions can be tested with regular GET/POST requests; server behavior is standard Django.
- The test settings ensure no posts to external services (`POST_TO_SOCIAL_MEDIA = False`).


## Quick reference
- Format code: `make pretty`
- Run server: `make run`
- Run tests: `make tests`

IMPORTANT: Always update README.md and this document as necessary when making changes.
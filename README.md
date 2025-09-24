# filamentcolors.xyz

The source code for filamentcolors.xyz — a small website for comparing pieces of printed filament and exploring color data. This repo includes the Django backend, REST API, templates, and frontend assets.

- Live site: https://filamentcolors.xyz/
- Public API root: https://filamentcolors.xyz/api/

## Overview

This project is a Django 5.x application managed with Poetry. It provides:
- A public JSON API for swatches and related data
- A server‑rendered frontend (Django templates) with progressive enhancement using HTMX and a bit of jQuery/vanilla JS
- Management commands for importing/curating data

The codebase favors small, focused modules and minimal dependencies beyond Django and a handful of utilities for color processing and images.

## Requirements

- Python >= 3.10, < 3.13
- Poetry (for dependency management and virtualenv)
- A working C toolchain for packages that need compilation (platform dependent)

Optional (used in development/tests/formatting):
- Make (for convenience commands)

## Setup

1) Clone the repository

2) Install dependencies
- poetry install

3) Configure settings
There are two common local approaches:
- EITHER set ENVIRONMENT=local to use filamentcolors.settings.local
- OR create a local_settings.py in the project root (same folder as manage.py). If present, it is automatically loaded and takes precedence.

Example local_settings.py:

```python
from filamentcolors.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "localhost"]
POST_TO_SOCIAL_MEDIA = False
```

4) Initialize the database (SQLite by default)
- poetry run python manage.py migrate
- Optional seed data (may take a bit):
  - poetry run python manage.py seed_swatches

## Running the app locally

- With Makefile: make run
- Or directly: poetry run python manage.py runserver

Entry points:
- Django manage script: manage.py
- WSGI app: filamentcolors.wsgi:application
- Settings router: filamentcolors.settings.routing (selects prod/local/local_settings based on ENVIRONMENT and presence of local_settings.py)

Note on static files:
- Authoring assets live in filamentcolors/appstatic
- Collected/static files are in filamentcolors/static (do not edit by hand)

## Scripts and common tasks

Make targets:
- make run — start dev server
- make migrate — apply migrations
- make tests — run test suite with coverage (xdist enabled)
- make pretty — run black and isort

Other helpers:
- format.sh — runs black and djade (template formatter) across templates

## Environment variables
These are read by settings; exact usage can be seen in filamentcolors/settings/*.py.

- ENVIRONMENT: Selects settings profile (local | prod). If unset and local_settings.py exists, that file is loaded; otherwise prod is used.
- DJANGO_SECRET_KEY: Secret key for Django (base.py provides a development default; set a strong value in production).
- ALTCHA_HMAC_KEY: HMAC key for Altcha challenges.
- DEBUG_MODE: Set to truthy value to enable DEBUG in base settings (use only in development).
- PLAUSIBLE_DOMAIN: Domain used by plausible_proxy.
- POST_TO_SOCIAL_MEDIA: Boolean flag; disabled in tests, enabled by default in base.
- BUGSNAG_KEY: API key used when running with prod settings to enable Bugsnag middleware.

Database configuration:
- Default DB is SQLite via base.py. For Postgres or other backends in production, override DATABASES in local_settings.py or a custom settings module. TODO: Document production DB configuration and environment variables if applicable.

## Testing

- Run all tests: make tests
  - Equivalent: poetry run pytest --cov --cov-report html
- Coverage HTML output: htmlcov/index.html

Notes:
- Tests run with DJANGO_SETTINGS_MODULE=filamentcolors.settings.testing (see pyproject.toml).
- A session‑scoped fixture seeds reference color data automatically; database access is enabled for tests by default.
- External side effects (e.g., social posting) are disabled in testing settings.

## Project structure (selected)

- filamentcolors/ — main Django app
  - settings/ — base, local, prod, testing, routing
  - api/ — REST API endpoints
  - templates/ — Django templates (partials/, modals/, standalone/)
  - appstatic/ — JS and CSS authored assets (e.g., js/components, css/main.css)
  - static/ — collected/static files (do not edit)
  - management/ — management commands (e.g., seed_swatches, importers)
  - tests/ — pytest test suite
  - helpers/constants/middleware/etc. — small support modules
- manage.py — Django entry point
- pyproject.toml — Poetry project, dependencies, and pytest config
- Makefile — convenience tasks

## Public API

Please give credit if you use this work for your project! Let me know if you do use this for something; I always love to see how this information is used!

API root: https://filamentcolors.xyz/api/

If you use the API for a project, please consider supporting server costs:
- Patreon: https://www.patreon.com/filamentcolors
- One‑time donation: https://buy.stripe.com/8wMbKg8UT4k8fBKaEE

API notes:

- Color family is marked by a 3‑letter code for data savings; the map can be found here: https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/models.py
- /api/swatch/ supports sort methods: type and manufacturer. See: https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/api/views.py
- Example URLs:
  - https://filamentcolors.xyz/api/swatch/?m=manufacturer
  - https://filamentcolors.xyz/api/swatch/?m=type

Please avoid hammering the API if you only need specific values; keep a cache of the information important to you. To validate your cache, request:
- GET https://filamentcolors.xyz/api/version/
- Example response: {"db_version": 1, "db_last_modified": 1586021667}
  - db_version increments on schema changes
  - db_last_modified is an ISO timestamp of the last swatch upload

Questions? Email [joe@filamentcolors.xyz](mailto:joe@filamentcolors.xyz).

## License

MIT © 2018–present Joe Kaufeld. See LICENSE for details.

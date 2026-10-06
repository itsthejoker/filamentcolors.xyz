# filamentcolors.xyz

[filamentcolors.xyz](https://filamentcolors.xyz/) is a library of real, printed filament swatches. Manufacturers always want to show you filament that looks pretty and worth spending your money on, but that doesn't match the real world. I print a swatch of each filament, photograph it under consistent lighting, and measure the printed plastic directly to get the actual color of the actual plastic. You can browse the library, compare swatches, find close matches to a color you already have, and find Pantone and RAL equivalents.

This repo holds the whole site: the Django app, the public API, the templates, and the frontend JS/CSS.

## Running it locally

You'll need Python 3.13+ and [Poetry](https://python-poetry.org/). A few dependencies build native extensions, so have a C toolchain handy if your platform doesn't ship wheels for them.

```shell
git clone https://github.com/itsthejoker/filamentcolors.xyz.git
cd filamentcolors.xyz
poetry install
```

Next, create `local_settings.py` in the repo root, next to `manage.py`:

```python
from filamentcolors.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "localhost"]
POST_TO_SOCIAL_MEDIA = False
```

The settings router (`filamentcolors/settings/routing.py`) looks for this file on startup. If it can't find it, it falls back to production settings, which is much less fun to debug with.

Then fill the database with fake data and start the server:

```shell
poetry run python manage.py seed_swatches
make run
```

`seed_swatches` runs migrations, asks you to create a superuser, imports the Pantone and RAL reference colors, and generates a pile of made-up manufacturers and swatches. It takes a minute. Once it finishes, the site lives at http://localhost:8000 and the admin at http://localhost:8000/admin/.

If you only want an empty database, `make migrate` does that instead.

### Where things live

| Path                                        | What's in it                                                                               |
|---------------------------------------------|--------------------------------------------------------------------------------------------|
| `filamentcolors/models.py`                  | Swatches, manufacturers, filament types, and friends                                       |
| `filamentcolors/views.py`, `staff_views.py` | Public pages and the staff-only upload/editing tools                                       |
| `filamentcolors/api/`                       | The DRF-powered public API                                                                 |
| `filamentcolors/templates/`                 | Django templates, with HTMX doing most of the interactive bits                             |
| `filamentcolors/appstatic/`                 | JS and CSS that you edit                                                                   |
| `filamentcolors/static/`                    | Output of `collectstatic`. Don't edit anything in here; your changes will get overwritten. |
| `filamentcolors/management/commands/`       | Seeding, importers, and maintenance scripts                                                |
| `filamentcolors/tests/`                     | The pytest suite                                                                           |

### Handy commands

- `make run` starts the dev server
- `make migrate` applies migrations
- `make tests` runs the test suite with coverage (HTML report lands in `htmlcov/`)
- `make test_all` also runs the Playwright browser tests (run `poetry run playwright install` once first)
- `make pretty` runs black and isort
- `./format.sh` runs black plus [djade](https://github.com/adamchainz/djade) on the templates

### Environment variables

You can skip all of these for local development; each one has a dev-safe default or only matters in production.

| Variable            | Purpose                                                                                                                           |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `ENVIRONMENT`       | Set to `local` to force `settings/local.py`. Otherwise the router uses `local_settings.py` if it exists, then falls back to prod. |
| `DJANGO_SECRET_KEY` | Django's secret key. The default exists for development only.                                                                     |
| `ALTCHA_HMAC_KEY`   | HMAC key for the [Altcha](https://altcha.org/) challenges on public forms.                                                        |
| `DEBUG_MODE`        | Any truthy value turns on `DEBUG` in the base settings.                                                                           |
| `BUGSNAG_KEY`       | Enables Bugsnag error reporting under prod settings.                                                                              |

The base settings use SQLite. Production runs on Postgres; override `DATABASES` in your own settings module if you want to do the same.

## Tests

```shell
make tests
```

Pytest picks up `filamentcolors.settings.testing` automatically (see `pyproject.toml`). That settings module turns off social media posting, and a session-scoped fixture loads the reference color data, so you don't have to set anything up first. Tests marked `playwright` get skipped unless you pass `--runplaywright`.

## The API

The API is free and public at https://filamentcolors.xyz/api/. If you build something with it, please give credit and drop me a line. I love seeing what people do with this data.

### Endpoints

- `/api/swatch/` lists swatches
- `/api/manufacturer/` lists manufacturers
- `/api/filament_type/` lists filament types
- `/api/pantone/` and `/api/ral/` list reference colors
- `/api/version/` tells you when the data last changed (more on that below)

### Searching and filtering swatches

| Parameter                          | Example                                | Notes                                                                                       |
|------------------------------------|----------------------------------------|---------------------------------------------------------------------------------------------|
| `q` (or `f`)                       | `q=orange`                             | Searches color name, manufacturer name, and filament type                                   |
| `m`                                | `m=color`                              | Sort order: `type`, `manufacturer`, `color`, or `random`. Leave it off to get newest first. |
| `manufacturer__slug`               | `manufacturer__slug=prusa`             | Add `__in` to pass a comma-separated list                                                   |
| `filament_type__parent_type__slug` | `filament_type__parent_type__slug=pla` | Also supports `__in`                                                                        |
| `td`                               | `td=0-30`                              | Transmission distance range as `min-max`                                                    |
| `page`, `page_size`                | `page_size=50`                         | Pages default to 15 swatches; you can ask for up to 100                                     |

Some examples:

- https://filamentcolors.xyz/api/swatch/?m=color
- https://filamentcolors.xyz/api/swatch/?m=manufacturer
- https://filamentcolors.xyz/api/swatch/?q=orange&manufacturer__slug=prusa&page_size=15

Color families come back as three-letter codes:

| Code  | Family | Code  | Family      |
|-------|--------|-------|-------------|
| `WHT` | White  | `BRN` | Brown       |
| `BLK` | Black  | `PPL` | Purple      |
| `RED` | Red    | `PNK` | Pink        |
| `GRN` | Green  | `RNG` | Orange      |
| `YLW` | Yellow | `GRY` | Grey        |
| `BLU` | Blue   | `TRN` | Translucent |

### Please cache

If you only need part of the data, grab it once and keep your own copy instead of hitting the API over and over. The API rate-limits requests, and the server bill comes out of my pocket. To check whether your copy is stale, call `GET /api/version/`:

```json
{"db_version": 1, "db_last_modified": 1586021667}
```

`db_last_modified` gives the Unix timestamp of the most recent swatch upload; if it hasn't changed, neither has the data. `db_version` only goes up when the API schema changes in a breaking way, and I'll announce that well ahead of time.

## Supporting the site

The site runs on my own dime. If you find it useful, especially if you're building on the API, you can chip in for server costs:

- [Patreon](https://www.patreon.com/filamentcolors)
- [One-time donation](https://buy.stripe.com/8wMbKg8UT4k8fBKaEE)

Questions, ideas, or bug reports: open an issue or email [joe@filamentcolors.xyz](mailto:joe@filamentcolors.xyz).

## Want to donate plastic?

Most of the library exists because people sent me filament. If you have one I don't, I'd love to add it. Search the [inventory](https://filamentcolors.xyz/inventory/) first, since I have plenty of plastic on hand that hasn't made it onto the site yet. If your filament doesn't show up, the [donation page](https://filamentcolors.xyz/donating/) walks you through it: cut at least 2 meters of each one, bag and label it, toss it in a padded envelope, and mail it over. I cover up to $100 a month in shipping reimbursements, so send me your receipt if you'd like one.

Want to print the swatches yourself? Email [joe@filamentcolors.xyz](mailto:joe@filamentcolors.xyz) and we'll work something out.

## License

MIT © 2018–present Joe Kaufeld. See [LICENSE](LICENSE).

# noinspection PyUnresolvedReferences
import os

from filamentcolors.settings.base import *  # noqa

# Ensure a clean, isolated DB behavior in tests
DATABASES["default"]["CONN_MAX_AGE"] = 0
DATABASES["default"]["TEST"] = {
    "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
}

# Disable debug toolbar in tests to avoid extra threads/hooks touching DB
INSTALLED_APPS = [a for a in INSTALLED_APPS if a != "debug_toolbar"]
MIDDLEWARE = [
    m for m in MIDDLEWARE if m != "debug_toolbar.middleware.DebugToolbarMiddleware"
]

ENVIRONMENT = "testing"
POST_TO_SOCIAL_MEDIA = False

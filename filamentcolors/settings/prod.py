# noinspection PyUnresolvedReferences
from filamentcolors.settings.base import *

ENVIRONMENT = "prod"
ALLOWED_HOSTS = ["*"]
BUGSNAG = {
    "api_key": os.environ.get("BUGSNAG_KEY"),
    "project_root": str(BASE_DIR),
}

MIDDLEWARE = ["bugsnag.django.middleware.BugsnagMiddleware"] + MIDDLEWARE

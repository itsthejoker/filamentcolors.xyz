"""
Django settings for filamentcolors project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import time

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "ssssh I'm hunting wabbits")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG_MODE", False)

ALLOWED_HOSTS = [".filamentcolors.xyz", "134.209.72.203"]
# INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, "images")
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "appstatic")]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "corsheaders",
    "debug_toolbar",
    # We don't use taggit anymore but removing it from the migrations is a pain
    # so I'm shoving that off on future me. Keeping it enabled for now.
    "taggit",
    "widget_tweaks",
    "filamentcolors",
    "rest_framework",
    "martor",
    "django_filters",
    "django_htmx",
    "plausible_proxy",
    "django_cleanup",  # This must be at the bottom!
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "filamentcolors.middleware.CacheControlMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "filamentcolors.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "filamentcolors.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    # There are no default throttles because there are some endpoints that need to remain
    # unthrottled and this is easier.
    "DEFAULT_THROTTLE_RATES": {
        # 600 requests per minute in bursts, or 5 requests a second over an hour.
        "burst": "600/min",
        "sustained": "18000/hour",
    },
}

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    "emoji": "true",  # to enable/disable emoji icons.
    "imgur": "true",  # to enable/disable imgur/custom uploader.
    "mention": "true",  # to enable/disable mention
    "jquery": "true",  # to include/revoke jquery (require for admin default django)
    "living": "false",  # to enable/disable live updates in preview
    "spellcheck": "true",  # to enable/disable spellcheck in form textareas
    "hljs": "true",  # to enable/disable hljs highlighting in preview
}

MARTOR_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.nl2br",
    "markdown.extensions.smarty",
    "markdown.extensions.fenced_code",
    # Custom markdown extensions.
    "martor.extensions.urlize",  # handle inline URLs
    "martor.extensions.del_ins",  # ~~strikethrough~~ and ++underscores++
    "filamentcolors.markdown_helpers.twitter_mention",  # to parse markdown mention
    "martor.extensions.emoji",  # to parse markdown emoji
    "martor.extensions.mdx_video",  # to parse embed/iframe video
    "filamentcolors.markdown_helpers.admonition",
    "filamentcolors.markdown_helpers.image_helper",
]

# To show the toolbar buttons
MARTOR_TOOLBAR_BUTTONS = [
    "bold",
    "italic",
    "horizontal",
    "heading",
    "pre-code",
    "blockquote",
    "unordered-list",
    "ordered-list",
    "link",
    "image-link",
    "image-upload",
    "emoji",
    "direct-mention",
    "toggle-maximize",
    "help",
]
MARTOR_SEARCH_USERS_URL = "/martor/search-user/"  # default

# Markdown Extensions
MARTOR_MARKDOWN_BASE_EMOJI_URL = "https://github.githubassets.com/images/icons/emoji/"
MARTOR_MARKDOWN_BASE_MENTION_URL = "https://twitter.com/"

MARTOR_UPLOAD_PATH = "images/uploads/{}".format(time.strftime("%Y/%m/%d/"))
MARTOR_UPLOAD_URL = "/api/uploader/"  # change to local uploader

# Maximum Upload Image
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_IMAGE_UPLOAD_SIZE = 5242880  # 5MB

CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PLAUSIBLE_DOMAIN = "filamentcolors.xyz"
FORMS_URLFIELD_ASSUME_HTTPS = True
POST_TO_SOCIAL_MEDIA = True

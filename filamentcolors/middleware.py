import os
import threading

from django.conf import settings
from django.core.signals import request_finished
from django.dispatch import receiver


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "HX-Request" in request.headers:
            response["Cache-Control"] = "no-store, max-age=0"

        return response


@receiver(request_finished)
def _close_db_connections_after_request(sender, **kwargs):
    """Optionally close DB connections at end of each request during UI tests.

    When running Playwright-driven UI tests (live_server), requests happen in a
    different thread. To avoid unclosed sqlite connection warnings at interpreter
    shutdown, we allow force-closing connections after each request — but only
    when explicitly enabled via env var so regular unit tests are unaffected.
    """
    if (
        getattr(settings, "ENVIRONMENT", None) == "testing"
        and os.environ.get("FC_CLOSE_DB_AFTER_REQUEST") == "1"
        # Only close connections for requests handled outside the main test thread
        # (i.e., live_server threads used by Playwright). Regular pytest-django
        # client requests run on the main thread and should keep their connection
        # lifecycle managed by pytest-django.
        and threading.current_thread() is not threading.main_thread()
    ):
        try:
            from django.db import connections

            connections.close_all()
        except Exception:
            # Don't disturb request lifecycle if closing fails for any reason
            pass

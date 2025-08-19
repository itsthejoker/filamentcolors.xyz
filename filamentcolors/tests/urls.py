from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.urls import include, path

handler400 = "filamentcolors.views.error_400"
handler404 = "filamentcolors.views.error_404"
handler500 = "filamentcolors.views.error_500"


def example_view(request, *args, **kwargs):
    pass


def fourzerofour(request):
    raise Http404


def fourhundred(request):
    raise SuspiciousOperation


def fivehundred(request):
    raise Exception


urlpatterns = [
    # stubs to make the tests pass
    path("", include("plausible_proxy.urls")),
    path("/", example_view, name="homepage"),
    path("library/", example_view, name="library"),
    path("mfr_list/", example_view, name="mfr_list"),
    path("about/", example_view, name="about"),
    path("about_us/", example_view, name="about_us"),
    path("donations/", example_view, name="donations"),
    path("monetary_donations/", example_view, name="monetary_donations"),
    path("monetary_donations/", example_view, name="colormatch"),
    path(
        "welcome_experience_image/<int:image_id>/",
        example_view,
        name="welcome_experience_image",
    ),
    path("welcome_experience_video", example_view, name="welcome_experience_video"),
    path("400/", fourhundred, name="400"),
    path("404/", fourzerofour, name="404"),
    path("500/", fivehundred, name="500"),
]

from django.urls import path

from filamentcolors.markdown_helpers.views import markdown_uploader

urlpatterns = [
    path(
        "api/uploader/",
        markdown_uploader, name='markdown_uploader_page'
    ),
]

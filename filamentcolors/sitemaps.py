from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['library', 'postlist', 'donations', 'about', 'inventory']

    def location(self, item):
        return reverse(item)

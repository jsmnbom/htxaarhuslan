# sitemaps.py
from django.contrib import sitemaps
from django.urls import reverse


class MainSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['index', 'info', 'turne', 'policy']

    def location(self, item):
        return reverse(item)

class TilmeldSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'hourly'

    def items(self):
        return ['tilmeld']

    def location(self, item):
        return reverse(item)


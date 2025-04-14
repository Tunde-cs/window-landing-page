from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["home", "submit_lead", "request_quote"]  # chatbot is on home page

    def location(self, item):
        return reverse(item)

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import BlogPost

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["home", "submit_lead", "request_quote", "ediomi_profile"]

    def location(self, item):
        return reverse(item)

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def location(self, obj):
        return f"/blog/{obj.slug}/"

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogPostSitemap,
}

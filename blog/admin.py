from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_published", "author")
    search_fields = ("title", "content")
    fields = ("title", "slug", "meta_description", "content", "author", "is_published")

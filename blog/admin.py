from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")  # ✅ keep "author" not "author_name"
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_published", "author")
    search_fields = ("title", "content")

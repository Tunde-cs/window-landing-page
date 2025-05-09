from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

def get_default_author():
    return User.objects.get(username="ediomi12").id

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional: Used for SEO and Google previews."
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_author)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

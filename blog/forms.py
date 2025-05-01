from django import forms
from blog.models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "slug", "content", "is_published"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }

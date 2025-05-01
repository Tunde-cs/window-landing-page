from django.shortcuts import render, get_object_or_404, redirect
from blog.models import BlogPost
from django.contrib.auth.decorators import login_required
from blog.forms import BlogPostForm

# 🌐 Public Blog List
def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

# 🌐 Public Blog Detail
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'blog/blog_detail.html', {'post': post})

# 👤 Employee-Only Blog Page (for Jane)
@login_required
def employee_blog_posts(request):
    # Only allow staff or Jane to access this view
    if not request.user.is_staff and request.user.username != "ediomi12":
        return redirect("useradmin")

    # Jane sees only her posts
    if request.user.username == "ediomi12":
        posts = BlogPost.objects.filter(author=request.user, is_published=True).order_by("-published_at")
        author_name = f"{request.user.first_name} {request.user.last_name}"
    else:
        # Other staff see all posts
        posts = BlogPost.objects.all().order_by("-published_at")
        author_name = "All Authors"

    context = {
        "posts": posts,
        "author_name": author_name,
    }

    return render(request, "employeePages/jane_blog_posts.html", context)


@login_required
def create_blog_post(request):
    if request.user.username != "ediomi12":
        return redirect("useradmin")

    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("employee_blog_posts")
    else:
        form = BlogPostForm()

    return render(request, "employeePages/blog_post_form.html", {"form": form, "edit": False})


@login_required
def edit_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id, author=request.user)

    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("employee_blog_posts")
    else:
        form = BlogPostForm(instance=post)

    return render(request, "employeePages/blog_post_form.html", {"form": form, "edit": True})


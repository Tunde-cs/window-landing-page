import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User  # ✅ Keep this for user-related functions
from .forms import LeadForm  # ✅ Import the correct form
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
import json


# ✅ Import Forms (Keep only if used in views)
from app.forms import (
    OrderForm,
    UserCreateForm,  # ✅ This replaces the built-in UserCreationForm
    LeadForm,
    QuoteForm,
    ReplyMessageForm,
)

# ✅ Import Models (Avoid duplicates)
from app.models import Lead, Message, Order, Project, Quote  # ✅ Keep only once

# Initialize logging
logger = logging.getLogger(__name__)


def home(request):
    """
    Handles GET and POST requests for the landing page:
    - Saves quotes to the database
    - Sends email confirmations
    - Displays success messages
    """
    print("DEBUG: User =", request.user)  # ✅ This will print the user in the console
    form = LeadForm()  # ✅ Create an empty form for GET requests

    if request.method == "POST":
        form = LeadForm(request.POST)  # ✅ Bind form with submitted data
        if form.is_valid():
            try:
                form.save()  # ✅ Save the form to the database
            except Exception as e:
                messages.error(request, "Failed to save your data. Please try again later.")
                logger.error(f"Database error: {e}")
                return render(request, "pages/index.html", {"form": form})

            # Send email
            try:
                send_mail(
                    subject="Quote Request Received",
                    message=f"Thank you, {form.cleaned_data['name']}, for reaching out to us!",
                    from_email="your-email@example.com",  # Replace with your email
                    recipient_list=[form.cleaned_data['email']],
                )
            except Exception as e:
                messages.error(
                    request, "Failed to send confirmation email. Please try again later."
                )
                logger.error(f"Email error: {e}")
                return render(request, "pages/index.html", {"form": form})

            # Redirect back to the landing page with a success message
            messages.success(
                request, "Thank you for your request. We'll get back to you soon!"
            )
            return redirect("home")

    # ✅ Always pass `form` in the context
    return render(request, "pages/index.html", {"form": form})  # ✅ Pass form to the template


@csrf_protect
def submit_lead(request):
     if request.method == "POST":
         email = request.POST.get("email")
         name = request.POST.get("name", "Anonymous")
         phone = request.POST.get("phone", None)
 
         if not email:
             messages.error(request, "Email is required.")
             return redirect("home")  # Redirect to landing page
 
         if Lead.objects.filter(email=email).exists():
             messages.error(request, "This email has already been submitted.")
             return redirect("home")
 
         try:
             # ✅ Save Lead
             new_lead = Lead.objects.create(name=name, email=email, phone=phone)
 
             # ✅ Test Email Sending & Print Errors
             subject = "Lead Submission Received"
             message = f"Dear {name},\n\nThank you for submitting your details. We'll contact you soon.\n\nPhone: {phone}"
             from_email = settings.DEFAULT_FROM_EMAIL
 
             send_mail(subject, message, from_email, [email], fail_silently=False)  # ❌ If error, it will be printed
 
             # ✅ Success Message
             messages.success(request, "Thank you! Your details have been submitted successfully.")
             return redirect("home")
 
         except Exception as e:
             print(f"❌ EMAIL ERROR: {e}")  # ✅ This will print the exact error
             messages.error(request, f"Error sending email: {e}")  # ✅ Show real error message
             return redirect("home")
 
     return render(request, "pages/index.html")


def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason})


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("useradmin")  # Replace with the appropriate redirect
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "registration/login.html")  # Ensure this template exists


# Template-based views
# About Us View
def about_page(request):
    return render(request, "pages/about.html")


def services_page(request):
    return render(request, "pages/services.html")


def contact_page(request):
    return render(request, "pages/contact.html")


# Terms of Use View
def terms_of_use_page(request):
    """Render the Terms of Use page."""
    return render(request, "pages/terms_of_use.html")


# Privacy Policy View
def privacy_policy(request):
    """Render the Privacy Policy page."""
    return render(request, "pages/privacy_policy.html")




@csrf_protect
def quick_lead_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Save email to the database as a new Lead or message
        try:
            Lead.objects.create(
                email=email, name="Anonymous"
            )  # Save email as "Anonymous"
            messages.success(
                request, "Thank you! Your email has been submitted successfully."
            )
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")

    return render(
        request, "pages/index.html"
    )  # Reload the user landing page with a success message


# Admin Login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("admin_home")  # Redirect to admin dashboard after login
        else:
            return render(
                request, "registration/login.html", {"error": "Invalid credentials"}
            )
    return render(request, "registration/login.html")  # Render login page


@csrf_protect
def request_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save()

            # 📩 Create a message for admin inbox
            Message.objects.create(
                 sender=quote.name,
                 receiver="admin",
                 subject="New Quote Submitted",
                 content=f"{quote.name} submitted a new quote request for {quote.service}.",
                 is_read=False
            )

            # Optional email
            send_mail(
                subject="Your Quote Request Has Been Received!",
                message=f"Dear {quote.name},\n\nThank you for requesting a quote. Our team will contact you soon.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[quote.email],
                fail_silently=True,
            )

            # Redirect back to landing or a success page
            return redirect("quote_success")
        else:
            messages.error(request, "There was an error submitting your request.")
    else:
        form = QuoteForm()

    return render(request, "pages/request_quote.html", {"form": form})


def quote_success(request):
    return render(request, "pages/quote_success.html")


# Admin Logout
@csrf_protect
def admin_logout(request):
    logout(request)  # Use Django's auth logout
    return redirect("admin_login")  # Redirect to admin login page


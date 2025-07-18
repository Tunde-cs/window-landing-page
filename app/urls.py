from django.urls import path,include
from django.views.generic import TemplateView
from . import views
from .views import home, submit_lead, request_quote
from .views import about_page, services_page, contact_page, terms_of_use_page, privacy_policy
from app.views import facebook_webhook
from .views import ediomi_profile


urlpatterns = [
    # ✅ Core Pages
    path("", home, name="index"),  # Route for the landing page
    path("request-quote/", views.request_quote, name="request_quote"),
    path("quote-success/", views.quote_success, name="quote_success"),  # Success page
    path("submit-lead/", submit_lead, name="submit_lead"),  # ✅ Email form submission

    # ✅ Public Pages
    path("about/", views.about_page, name="about"),
    path("services/", views.services_page, name="services"),
    path("contact/", views.contact_page, name="contact"),
    path("terms-of-use/", views.terms_of_use_page, name="terms_of_use"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    

    path('saas/', views.saas_landing, name='saas_landing'),
    path('facebook/webhook/', views.facebook_webhook, name='facebook_webhook'),

    path("ediomi-iyanam/", ediomi_profile, name="ediomi_profile"),

            
    path("api/", include("chatbot.urls")),  # ✅ Now chatbot API is accessible via /api/chat/

    # Optional: Generic landing page route
    path("", TemplateView.as_view(template_name="pages/index.html"), name="landing_page"),
]

from django.views.static import serve
from django.conf import settings
from django.urls import re_path

urlpatterns += [
    re_path(r'^favicon\.ico$', serve, {
        'path': 'assets/favicon.ico',
        'document_root': settings.STATIC_ROOT,
    }),
]

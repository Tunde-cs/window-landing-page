from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from LPageToAdmin.views import mark_message_read
from LPageToAdmin.views import reply_message  # Ensure function is imported
from .views import logout_view
from LPageToAdmin.views import signup  # ✅ Import the correct signup view
from LPageToAdmin.views import USERADMIN  # ✅ Make sure USERADMIN is properly imported
from .views import admin_dashboard, employee_dashboard,projects_view
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from .views import send_email  # Import the new function
from LPageToAdmin.views import custom_password_reset_done
from .views import mark_order_complete
from app.forms import OrderForm
from LPageToAdmin.views import mark_order_pending
from LPageToAdmin.views import update_profile_picture
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from app.sitemaps import StaticViewSitemap


from . import views
from app import views as app_views  # Import app-level views
from LPageToAdmin.views import (
    pending_orders_view,
    order_delete,
    admin_leads_view,
)

# Import views from LPageToAdmin
from .views import (
    USERADMIN,
    revenue_view,
    reports_view,
    reports_export,
    orders_view,
    view_order,
    edit_order,
    order_delete,
    admin_submit_lead,
    delete_lead,
    delete_message,
    admin_inbox,
    admin_quotes_view,
    delete_quote,
    view_message,
)

# ✅ Sitemap dictionary
sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    # ✅ Django Admin Panel
    path("admin/", admin.site.urls),
            
    # ✅ Base Pages
    path("base/", views.BASE, name="base"),  # Base page
    path("adminpage/base/", views.ADMINBASE, name="adminbase"),  # Admin base
    path("", views.HOME, name="home"),  # Landing page
    path("useradmin/", views.USERADMIN, name="useradmin"),  # Admin dashboard
    path("useradmin/send-email/", send_email, name="send_email"),  # ✅ Add email send route
        
    # ✅ Authentication
    path("signup/", views.signup, name="signup"),  # Signup page
    path("logout/", logout_view, name="logout"),  # ✅ Correct Logout Route
    path("accounts/", include("django.contrib.auth.urls")),  # Default Django authentication
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login"
    ),

    # ✅ Reports
    path("reports/", views.reports_view, name="reports"),
    path("reports/export/", reports_export, name="reports_export"),  # Export route
    path("revenue/", revenue_view, name="revenue"),  # Corrected path

    # ✅ Messages & Leads Management
    path("view_message/<int:message_id>/", views.view_message, name="view_message"),
    path("mark_message_read/<int:message_id>/", views.mark_message_read, name="mark_message_read"),
    path("reply_message/<int:message_id>/", reply_message, name="reply_message"),
    path("adminleads/", views.admin_submit_lead, name="adminleads"),  # Admin leads view
    path("adminleads/delete/<int:lead_id>/", delete_lead, name="delete_lead"),
    path("adminmessages/delete/<int:message_id>/", delete_message, name="delete_message"),
    path("admininbox/", admin_inbox, name="admininbox"),
    path("adminleads/", admin_leads_view, name="adminleads"),
    path("adminprojects/", projects_view, name="adminprojects"),
    path("adminmessages/", admin_inbox, name="admin_inbox"),


    # ✅ Admin Quotes Management
    path("adminquotes/", admin_quotes_view, name="adminquotes"),  # Main admin quotes view
    path("adminquotes/<int:quote_id>/", admin_quotes_view, name="adminquote_detail"),  # Specific quote
    path("adminquotes/delete/<int:quote_id>/", delete_quote, name="delete_quote"),  # Delete a quote
    path("quote/<int:quote_id>/pending/", views.mark_quote_pending, name="mark_quote_pending"),
    path("quote/<int:quote_id>/active/", views.mark_quote_active, name="mark_quote_active"),
    path("quote/<int:quote_id>/completed/", views.mark_quote_completed, name="mark_quote_completed"),


    # ✅ Orders Management
    path("orders/", orders_view, name="orders"),
    path("orders/pending/", pending_orders_view, name="pending_orders"),  # Pending orders
    path("orders/pending/<int:order_id>/", mark_order_pending, name="mark_order_pending"),
    path("orders/<int:order_id>/", view_order, name="view_order"),
    path("orders/<int:order_id>/complete/", mark_order_complete, name="mark_order_complete"),
    path("orders/edit/<int:id>/", edit_order, name="edit_order"),
    path("orders/delete/<int:order_id>/", order_delete, name="order_delete"),

    path("profile/", update_profile_picture, name="update_profile_picture"),

    # ✅ Sitemap route
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("google126635fbdb4f1c73.html", TemplateView.as_view(template_name="google126635fbdb4f1c73.html", content_type="text/html")),


    # ✅ Password Reset URLs
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset.html"
    ), name="password_reset"),

    path("password-reset/done/", custom_password_reset_done, name="password_reset_done"),

    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),

    # ✅ Include app-level URLs (Landing Page)
    path("", include("app.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Add static file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

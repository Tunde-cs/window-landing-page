from django.contrib import admin
from .models import Lead, Order, Project, Quote  # No need to add 'app'
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile  # ✅ Import the model
from .models import FacebookLead


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "amount", "date")
    list_filter = ("status", "date")
    search_fields = ("id", "status")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "window_style", "status")
    list_filter = ("status",)
    search_fields = ("window_style",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "city", "state", "financing", "submitted_at")
    search_fields = ("name", "email")
    

    # ✅ Add custom admin action
    actions = ["send_email"]

    def send_email(self, request, queryset):
        """Send email to selected users in Admin"""
        sent_count = 0  # ✅ Track emails sent
        for quote in queryset:
            if quote.email:  # ✅ Ensure email is not empty
                send_mail(
                    subject="Follow-Up on Your Quote Request",
                    message=f"Dear {quote.name},\n\nWe are following up on your recent quote request. Let us know how we can assist you further.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[quote.email],
                    fail_silently=True,
                )
                sent_count += 1  # ✅ Increment count if email sent

        self.message_user(request, f"✅ {sent_count} email(s) sent successfully!")

    send_email.short_description = "📩 Send follow-up email to selected users"
    

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "service",
        "status",
        "created_at",
        "is_active",
    )  # Includes all necessary fields
    list_filter = (
        "status",
        "service",
        "created_at",
    )  # Added 'service' for filtering by type of service
    search_fields = ("name", "email", "phone", "service")  # Remains unchanged

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "profile_picture")
    list_filter = ("role",)
    search_fields = ("user__username", "role")

@admin.register(FacebookLead)
class FacebookLeadAdmin(admin.ModelAdmin):
    list_display = ("leadgen_id", "full_name", "email", "phone_number", "created_time")
    search_fields = ("full_name", "email", "phone_number", "leadgen_id")
    list_filter = ("created_time",)


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
    )

    customer_name = models.CharField(max_length=255, default="Unknown")  # ✅ Added this field
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name} - {self.status} - ${self.amount}"
    

# Project Model
class Project(models.Model):
    window_style = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        choices=(("completed", "Completed"), ("in-progress", "In Progress")),
    )

    def __str__(self):
        return self.window_style


SERVICE_CHOICES = [
    ('window_replacement', 'Window Replacement'),
    ('door_installation', 'Door Installation'),
    ('roof_repair', 'Roof Repair'),
]

class Quote(models.Model):
    WINDOW_TYPES = (
        ("double_hung", "Double Hung"),
        ("casement", "Casement"),
        ("sliding", "Sliding"),
        ("bay_bow", "Picture"),
        ("custom", "Custom"),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    service = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    windowType = models.CharField(max_length=50, choices=WINDOW_TYPES)
    details = models.TextField(blank=True)

    # 🏡 Location Fields
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    property_address = models.CharField(max_length=255, blank=True)

    # 💰 Financing Option (Yes/No)
    financing = models.BooleanField(null=True, blank=True)

    # 📅 Timestamp
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service}"
    
    
class Lead(models.Model):
    SERVICES = (
        ("window_replacement", "Window Replacement"),
        ("door_installation", "Door Installation"),
        ("roof_repair", "Roof Repair"),
    )
    STATUSES = (
        ("new", "New"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
    )

    name = models.CharField(max_length=100, blank=False, validators=[MinLengthValidator(2)])
    email = models.EmailField(blank=False)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(r"^\+?\d{9,15}$", "Enter a valid phone number with 9 to 15 digits.")
        ],
    )
    service = models.CharField(max_length=100, choices=SERVICES, default="window_replacement")
    status = models.CharField(max_length=50, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:  # ✅ Move `Meta` inside `Lead`
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"


class Message(models.Model):
    sender = models.CharField(max_length=100, verbose_name="Sender Name")  # Sender name
    receiver = models.CharField(
        max_length=100, verbose_name="Receiver Name"
    )  # Receiver name
    subject = models.CharField(
        max_length=200, verbose_name="Message Subject"
    )  # Subject of the message
    content = models.TextField(verbose_name="Message Content")  # Message content
    is_read = models.BooleanField(
        default=False, verbose_name="Read Status"
    )  # Read/unread status
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At"
    )  # Timestamp for creation

    class Meta:
        ordering = ["-created_at"]  # Order messages by newest first
        verbose_name = "Message"  # Friendly name in Django admin
        verbose_name_plural = "Messages"  # Plural name in Django admin

    def mark_as_read(self):
        """Mark the message as read."""
        self.is_read = True
        self.save()

    def update_read_status(self, read_status=True):
        """Update the read/unread status of the message."""
        self.is_read = read_status
        self.save()

    def __str__(self):
        return f"{self.subject} ({'Read' if self.is_read else 'Unread'})"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default-profile.png')

    def __str__(self):
        return self.user.username
    
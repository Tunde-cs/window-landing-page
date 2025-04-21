from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
    )

    customer = models.ForeignKey('Quote', on_delete=models.CASCADE, related_name='orders')
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    number_of_windows = models.PositiveIntegerField(default=1)
    window_type = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)  # ✅ Add this
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.name} - {self.status} - ${self.amount}"


# Project Model
class Project(models.Model):
    STATUS_CHOICES = (
        ("completed", "Completed"),
        ("in-progress", "In Progress"),
    )

    window_style = models.CharField(max_length=100, choices=[("double_hung", "Double Hung"), ("casement", "Casement")], blank=False)  # Choices for window styles
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="in-progress")  # Default status is in-progress

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"Project - {self.window_style} - {self.status}"



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
        ("picture", "Picture"),
        ("custom", "Custom"),
    )

    STATUS_CHOICES = (
        ("new", "New"),
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
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

    # 📦 Quote Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

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
    receiver = models.CharField(max_length=100, verbose_name="Receiver Name")  # Receiver name
    subject = models.CharField(max_length=200, verbose_name="Message Subject")  # Subject of the message
    content = models.TextField(verbose_name="Message Content")  # Message content
    is_read = models.BooleanField(default=False, verbose_name="Read Status")  # Read/unread status
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")  # Timestamp for creation

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
    


class ChatbotLead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"



class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("Employee", "Employee"),
        ("Admin", "Admin"),
        ("Sales", "Sales"),
        ("Technician", "Technician"),
        ("Manager", "Manager"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Employee")  # ✅ Added roles

    def __str__(self):
        return self.user.username
    
    
class FacebookLead(models.Model):
    leadgen_id = models.CharField(max_length=255)
    page_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name if self.full_name else self.leadgen_id

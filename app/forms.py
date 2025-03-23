from django import forms
from .models import Lead, Message, Quote  # Import your models here
from .models import Order
from app.models import Lead  # Ensure this imports the correct Lead model
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from app.models import UserProfile  # ✅ Ensure UserProfile model exists
from .models import SERVICE_CHOICES


# ✅ Custom User Registration Form
class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # ✅ Mark as staff so they can access the admin page

        if commit:
            user.save()
            # ✅ Ensure the "Employees" group exists before adding
            employee_group, created = Group.objects.get_or_create(name="Employees")
            user.groups.add(employee_group)  # ✅ Add user to "Employees" group

        return user
    
class LeadForm(forms.Form):  # Change from ModelForm to Form
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control form-control-lg",  # Matches your Bootstrap styling
        "id": "email",  # Matches your HTML input field
        "placeholder": "Email Address",  # User-friendly placeholder
        "required": "required",  # Ensures the field is required
    }))
    

class QuoteForm(forms.ModelForm):
    # Define SERVICE_CHOICES at the top
    SERVICE_CHOICES = [
        ('window_replacement', 'Window Replacement'),
        ('door_installation', 'Door Installation'),
        ('roof_repair', 'Roof Repair'),
    ]

    class Meta:
        model = Quote
        fields = [
            "name",
            "email",
            "phone",
            "service",  # This field will use the dropdown menu
            "windowType",
            "details",
            "city",
            "state",
            "zipcode",
            "property_address",
            "financing",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Customer Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Customer Email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "service": forms.Select(choices=SERVICE_CHOICES, attrs={"class": "form-select"}),  # Dropdown for services
            "windowType": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(attrs={"class": "form-control", "placeholder": "Additional Details (Optional)"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City (Optional)"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "State (Optional)"}),
            "zipcode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Zip Code (Optional)"}),
            "property_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Property Address (Optional)"}),
            "financing": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        def clean_financing(self):
            financing = self.cleaned_data.get("financing")
            if financing == "yes":
                return True
            elif financing == "no":
                return False
            return None  # or False based on your logic



    
class ReplyMessageForm(forms.Form):
    subject = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["date", "amount", "status"]  # Ensure these fields match the model


    
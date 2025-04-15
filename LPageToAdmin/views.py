from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages  # Import the messages framework
from django.contrib.auth.decorators import login_required
from app.forms import LeadForm  # Ensure LeadForm is correctly imported
from datetime import datetime
from django import forms
import re
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from app.forms import QuoteForm
from app.models import Quote
from django.http import HttpResponse
import csv
from app.models import Message
from calendar import month_name
from django.urls import reverse
from app.models import Order, Customer
import json  # ✅ Import json module
import calendar
from django.contrib.auth.models import User
from django.http import HttpResponse
from app.forms import UserCreateForm  # ✅ Import from app/forms.py
from django.template.response import TemplateResponse  # ✅ Import TemplateResponse
from django.db.models.functions import ExtractMonth
from django.contrib.auth.decorators import user_passes_test
from app.models import Lead, Message, Order, Project, Quote  # ✅ Models only
from app.forms import UserCreateForm  # ✅ Import UserCreateForm from forms.py
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from app.forms import OrderForm
from app.forms import ProfilePictureForm
from app.models import UserProfile
from django.utils import timezone



# Base Views
def BASE(request):
    return render(request, "base/base.html")


def ADMINBASE(request):
    return render(request, "base/adminbase.html")


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='/')(
        view_func
    )


# Home View
def HOME(request):
    """Renders the homepage with user info."""
    context = {
        "user": request.user,  # ✅ Add this line
        "static_example": "/static/assets/img/testimonial-1.jpg",
    }
    return render(request, "pages/index.html", context)


# User Registration (Signup)
def signup(request):
    form = UserCreateForm()  # ✅ Always create a form instance

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.first_name = form.cleaned_data["first_name"]
            new_user.last_name = form.cleaned_data["last_name"]
            new_user.save()
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return redirect("useradmin")

    return render(request, "registration/signup.html", {"form": form})


# Email Utility
def send_quote_email(to_email, subject, message):
    """Send a quote email using Django's send_mail function."""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
    )


@csrf_protect
@login_required
def USERADMIN(request):
    if request.user.is_superuser:
        return redirect("/admin/")  # Superuser sees Django admin
    elif request.user.username == "ediomi12":
        return employee_dashboard(request)  # 👈 DIRECTLY call the employee dashboard
    elif request.user.is_staff:
        return admin_dashboard(request)     # 👈 DIRECTLY call the admin dashboard
    else:
        return redirect("login")  # Or show custom error
    

def admin_dashboard(request):
    """Admin Dashboard View - Displays key metrics, recent leads, and sales data."""
    
    user = request.user
    context = {
        "user": user,
        "request": request,
        "unread_messages": Message.objects.filter(is_read=False).count(),
    }
    
    try:
        # ✅ Fetch main admin-related metrics
        new_leads_count = Lead.objects.filter(status="new").count()
        active_quotes_count = Quote.objects.filter(status="active").count()
        new_quote_count = Quote.objects.filter(status="new").count()
        quote_leads_count = Quote.objects.count() 
        pending_orders_count = Order.objects.filter(status="pending").count()
        completed_projects_count = Order.objects.filter(status="completed").count()
        monthly_revenue = (
            Order.objects.filter(date__month=now().month)
            .aggregate(Sum("amount"))
            .get("amount__sum", 0)
            or 0
        )
        total_quotes = Quote.objects.count()
        orders_in_progress = Order.objects.filter(status="in-progress").count()
        sales_completed = Order.objects.filter(status="completed").count()
        message_count = Message.objects.filter(is_read=False).count()

        # ✅ Conversion Rate Calculation
        total_leads = Lead.objects.count()
        conversion_rate = round((sales_completed / total_leads) * 100, 2) if total_leads > 0 else 0

        # ✅ Fetch Monthly Sales Data
        raw_sales_data = (
            Order.objects.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        # ✅ Fetch Monthly Quote Requests Data
        raw_quote_data = (
            Quote.objects.annotate(month=ExtractMonth("submitted_at"))
            .values("month")
            .annotate(total=Count("id"))  # Count number of quote requests
            .order_by("month")
        )

        # ✅ Ensure all 12 months have data
        sales_data_dict = {data["month"]: float(data["total"]) for data in raw_sales_data if data["month"]}
        quote_data_dict = {data["month"]: int(data["total"]) for data in raw_quote_data if data["month"]}

        # ✅ Create the 12-month structured lists
        sales_chart_labels = []
        sales_chart_data = []
        quote_chart_data = []

        for month in range(1, 13):  # Loop through all 12 months
            sales_chart_labels.append(month_name[month])  # Convert number to month name
            sales_chart_data.append(sales_data_dict.get(month, 0))  # Get sales or default to 0
            quote_chart_data.append(quote_data_dict.get(month, 0))  # Get quote requests or default to 0

        # ✅ Convert Data to JSON for Frontend
        context.update({
            "metrics": {
                "new_leads_count": new_leads_count + quote_leads_count,
                "active_quotes_count": active_quotes_count,
                "pending_orders_count": pending_orders_count,
                "completed_projects_count": completed_projects_count,
                "monthly_revenue": monthly_revenue,
                "total_quotes": total_quotes,
                "orders_in_progress": orders_in_progress,
                "sales_completed": sales_completed,
                "conversion_rate": conversion_rate,
                "message_count": message_count,
            },
            "sales_chart_labels": json.dumps(sales_chart_labels),
            "sales_chart_data": json.dumps(sales_chart_data),
            "quote_chart_data": json.dumps(quote_chart_data),
        })

    except Exception as e:
        print(f"Error fetching data: {e}")  # Debugging error
        context.update({
            "metrics": {
                "new_leads_count": 0,
                "pending_orders_count": 0,
                "completed_projects_count": 0,
                "monthly_revenue": 0.0,
                "total_quotes": 0,
                "orders_in_progress": 0,
                "sales_completed": 0,
                "conversion_rate": 0,
                "message_count": 0,
            },
            "sales_chart_labels": json.dumps(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]),
            "sales_chart_data": json.dumps([0] * 12),
            "quote_chart_data": json.dumps([0] * 12),
        })

    # ✅ Always add new_quote_count to the final context, no matter what    
    context["new_quote_count"] = new_quote_count
    return TemplateResponse(request, "adminPages/adminhome.html", context)


def employee_dashboard(request):
    print("🔍 View: employee_dashboard")
    print("Template path: employeePages/employee_dashboard.html")
    print("Extends from:", "base/adminbase.html")
    
    """Employee Dashboard View - Mirrors Admin Dashboard Metrics but shows employee-specific template"""

    user = request.user

    # 🔐 Prevent access from 'admin' account
    if user.username == "admin":
        return redirect("admin_dashboard")

    context = {
        "user": user,
        "request": request,
        "unread_messages": Message.objects.filter(is_read=False).count(),
    }

    try:
        # ✅ Metrics
        new_leads_count = Lead.objects.filter(status="new").count()
        active_quotes_count = Quote.objects.filter(status="active").count()
        quote_leads_count = Quote.objects.count() 
        pending_orders_count = Order.objects.filter(status="pending").count()
        completed_projects_count = Order.objects.filter(status="completed").count()
        monthly_revenue = (
            Order.objects.filter(date__month=now().month)
            .aggregate(Sum("amount"))
            .get("amount__sum", 0)
            or 0
        )
        total_quotes = Quote.objects.count()
        orders_in_progress = Order.objects.filter(status="in-progress").count()
        sales_completed = Order.objects.filter(status="completed").count()
        message_count = Message.objects.filter(is_read=False).count()

        total_leads = Lead.objects.count()
        conversion_rate = round((sales_completed / total_leads) * 100, 2) if total_leads > 0 else 0

        # ✅ Sales Data
        raw_sales_data = (
            Order.objects.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        # ✅ Quote Data
        raw_quote_data = (
            Quote.objects.annotate(month=ExtractMonth("submitted_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        sales_data_dict = {data["month"]: float(data["total"]) for data in raw_sales_data if data["month"]}
        quote_data_dict = {data["month"]: int(data["total"]) for data in raw_quote_data if data["month"]}

        sales_chart_labels = []
        sales_chart_data = []
        quote_chart_data = []

        for month in range(1, 13):
            sales_chart_labels.append(month_name[month])
            sales_chart_data.append(sales_data_dict.get(month, 0))
            quote_chart_data.append(quote_data_dict.get(month, 0))

        # ✅ Add to context
        context.update({
            "metrics": {
                "new_leads_count": new_leads_count + quote_leads_count,
                "active_quotes_count": active_quotes_count,
                "pending_orders_count": pending_orders_count,
                "completed_projects_count": completed_projects_count,
                "monthly_revenue": monthly_revenue,
                "total_quotes": total_quotes,
                "orders_in_progress": orders_in_progress,
                "sales_completed": sales_completed,
                "conversion_rate": conversion_rate,
                "message_count": message_count,
            },
            "sales_chart_labels": json.dumps(sales_chart_labels),
            "sales_chart_data": json.dumps(sales_chart_data),
            "quote_chart_data": json.dumps(quote_chart_data),
        })

    except Exception as e:
        print(f"Error fetching employee dashboard data: {e}")
        context.update({
            "metrics": {
                "new_leads_count": 0,
                "pending_orders_count": 0,
                "completed_projects_count": 0,
                "monthly_revenue": 0.0,
                "total_quotes": 0,
                "orders_in_progress": 0,
                "sales_completed": 0,
                "conversion_rate": 0,
                "message_count": 0,
            },
            "sales_chart_labels": json.dumps(sales_chart_labels),
            "sales_chart_data": json.dumps(sales_chart_data),
            "quote_chart_data": json.dumps(quote_chart_data),
        })
        print("✅ sales_chart_data:", sales_chart_data)


    return TemplateResponse(request, "employeePages/employee_dashboard.html", context)


# Sidebar Views
@staff_member_required
def admin_leads_view(request):
    if request.method == "POST":
        # Handle the form submission
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        service = request.POST.get("service")

        # Save the new lead
        Lead.objects.create(name=name, email=email, phone=phone, service=service)
        messages.success(request, "Lead successfully submitted!")

        # Redirect to the same page after form submission
        return redirect("adminPages/adminleads")

    # Fetch all leads to display
    leads = Lead.objects.all()
    return render(request, "adminPages/adminleads.html", {"leads": leads})


def revenue_view(request):
    """
    Handles the revenue details view.
    """
    # Example revenue data (replace with actual database query)
    revenue_data = [
        {"month": "January", "total": 43300.33},
        {"month": "February", "total": 50200.12},
        {"month": "March", "total": 39000.45},
    ]  # Sample monthly revenue

    return render(request, "adminPages/revenue.html", {"revenue_data": revenue_data})


@login_required
def pending_orders_view(request):
    if not request.user.is_staff:  # Ensure only staff/admin users can access
        return redirect("admin:login")

    pending_orders = Order.objects.filter(status="pending")
    pending_orders_count = pending_orders.count()

    return render(
        request,
        "adminPages/adminorders.html",
        {
            "orders": pending_orders,
            "pending_orders_count": pending_orders_count,
            "view_mode": "pending",
        },
    )


@csrf_protect
def orders_view(request):
    """
    View for managing all orders, including pending orders, dynamically.
    """
    if not request.user.is_staff:  # Restrict access to staff/admin users
        return redirect("admin:login")

    # Get the filter type from the query parameter
    view_mode = request.GET.get("view", "all")  # Default to 'all'

    if view_mode == "pending":
        orders = Order.objects.filter(status="pending")  # Filter for pending orders
        pending_orders_count = orders.count()
    else:
        orders = Order.objects.all()  # Fetch all orders
        pending_orders_count = None

    # Pass the orders and metrics to the template
    return render(
        request,
        "adminPages/adminorders.html",
        {
            "orders": orders,
            "view_mode": view_mode,
            "pending_orders_count": pending_orders_count,
        },
    )

def edit_order(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order {order.id} updated successfully!")
            return redirect("view_order", order_id=order.id)
    else:
        form = OrderForm(instance=order)

    return render(request, "adminPages/edit_order.html", {"form": form})


@csrf_protect
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "adminPages/order_details.html", {"order": order})


@csrf_protect
@login_required
def mark_order_pending(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "pending"
    order.save()
    messages.info(request, f"Order {order.id} marked as pending.")
    return redirect("view_order", order_id=order.id)


@csrf_protect
def mark_order_complete(request, order_id):
    """Marks a specific order as completed."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.status = "completed"
        order.save()
    return redirect("view_order", order_id=order_id)


def order_delete(request, order_id):
    """
    Deletes a specific order by ID and redirects to the orders list with a success message.
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this order.")
        return redirect("orders")  # Redirect to all orders page

    # Get the order or return 404 if it doesn’t exist
    order = get_object_or_404(Order, id=order_id)
    order.delete()

    # ✅ Add a success message
    messages.success(request, f"Order {order_id} deleted successfully.")

    # ✅ Redirect to the correct orders page
    return redirect("orders")  # Ensure this matches your URLs


# views.py
def projects_view(request):
    completed_orders = Order.objects.filter(status="completed")
    return render(request, "adminPages/adminprojects.html", {"projects": completed_orders})


def reports_view(request):
    """Handles generating reports with actual order data."""

    # Get optional date filters from request
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Retrieve all orders (filtered if necessary)
    orders = Order.objects.all()
    if start_date and end_date:
        orders = orders.filter(date__range=[start_date, end_date])

    # Aggregate report data
    total_revenue = round(orders.aggregate(Sum("amount"))["amount__sum"] or 0, 2)
    total_orders = orders.count()
    pending_orders = orders.filter(status="pending").count()
    total_customers = Customer.objects.count()

    # Convert orders into report data
    report_data = list(orders.values("id", "status", "amount", "date"))

    # Prepare sales data for the chart
    sales_data = (
        Order.objects.filter(date__year=now().year)
        .values("date__month")
        .annotate(total_sales=Sum("amount"))
        .order_by("date__month")
    )

    # Convert sales data to JSON for Chart.js
    sales_chart_labels = [f"{data['date__month']}" for data in sales_data]
    sales_chart_data = [float(data["total_sales"]) for data in sales_data]

    return render(
        request,
        "adminPages/adminreports.html",
        {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_customers": total_customers,
            "report_data": report_data,
            "start_date": start_date,
            "end_date": end_date,
            "sales_chart_labels": json.dumps(sales_chart_labels),
            "sales_chart_data": json.dumps(sales_chart_data),
        },
    )


def reports_export(request):
    """Export reports to CSV format with real order data."""
    # Retrieve order data
    orders = Order.objects.all()

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reports.csv"'

    # Write CSV headers and data
    writer = csv.writer(response)
    writer.writerow(["Order ID", "Status", "Amount", "Date"])
    for order in orders:
        writer.writerow([order.id, order.status, order.amount, order.date])

    return response


@csrf_protect
def projects_view(request):
    completed_orders = Order.objects.filter(status="completed")
    return render(request, "adminPages/adminprojects.html", {"projects": completed_orders})


# Admin Inbox View
@staff_member_required
def admin_inbox(request):
    inbox_messages = Message.objects.order_by("-created_at")  # ✅ Rename this
    leads = Lead.objects.order_by("-created_at")

    context = {
        "inbox_messages": inbox_messages,  # ✅ Renamed
        "leads": leads,
        "message_count": inbox_messages.count(),
        "lead_count": leads.count(),
    }
    return render(request, "adminPages/admininbox.html", context)



@csrf_protect
def quick_lead_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            Lead.objects.create(email=email, name="Anonymous")
            messages.success(request, "Your email has been submitted successfully!")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
    return render(request, "user_landing.html")  # Ensure this template exists
    path(
        "userlanding/", views.user_landing, name="user_landing"
    ),  # Define the URL pattern


@csrf_protect
@login_required
def view_message(request, message_id):
    """Handles viewing a specific message."""
    message = get_object_or_404(Message, id=message_id)

    # Mark the message as read when viewed
    if not message.is_read:
        message.is_read = True
        message.save()

    return render(request, "adminPages/adminmessage_detail.html", {"message": message})

@login_required
def mark_message_read(request, message_id):
    """Marks a message as read when the admin clicks the 'Mark as Read' button."""
    message = get_object_or_404(Message, id=message_id)
    
    if not message.is_read:
        message.is_read = True
        message.save()

    return redirect("view_message", message_id=message.id)  # Ensure this URL name exists

@login_required
def reply_message(request, message_id):
    """Handles replying to a message."""
    message = get_object_or_404(Message, id=message_id)

    if request.method == "POST":
        reply_content = request.POST.get("reply_content")
        if reply_content:
            # Create a new reply message (or update existing logic)
            reply = Message.objects.create(
                sender=request.user.username,  # Assume sender is the logged-in user
                receiver=message.sender,  # Send reply back to the original sender
                subject=f"Re: {message.subject}",  # Prefix subject with "Re:"
                content=reply_content,
                is_read=False,  # Mark new reply as unread
            )
            messages.success(request, "Reply sent successfully!")
            return redirect("view_message", message_id=message.id)

    messages.error(request, "Failed to send reply. Please try again.")
    return redirect("view_message", message_id=message.id)


# Ensure only admin users can access this view
@csrf_protect
@staff_member_required
def admin_submit_lead(request):
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name", "Anonymous")
        phone = request.POST.get("phone", "")
        service = request.POST.get("service", "window_replacement")  # ✅ Add this

        # Validate
        if not email:
            messages.error(request, "Email is required.")
            return redirect("adminleads")

        if phone and not re.match(r"^\+?\d{9,15}$", phone):
            messages.error(request, "Invalid phone number format.")
            return redirect("adminleads")

        if Lead.objects.filter(email=email).exists():
            messages.error(request, "This email has already been submitted.")
        else:
            try:
                Lead.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    service=service,  # ✅ Now included
                    status="new"
                )
                messages.success(request, "Lead submitted successfully!")
            except Exception as e:
                print(f"Error saving lead: {str(e)}")
                messages.error(request, "An error occurred while saving the lead. Please try again.")

        return redirect("adminleads")

    leads = Lead.objects.all().order_by("-created_at")
    return render(request, "adminPages/adminleads.html", {"leads": leads})


@csrf_protect
def admin_quotes_view(request, quote_id=None):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote added successfully!")
        else:
            messages.error(request, "Error adding quote. Please check the form.")

    quote = None
    if quote_id:
        quote = get_object_or_404(Quote, id=quote_id)

    status_filter = request.GET.get("status")
    if status_filter in ["new", "pending", "active", "completed"]:
        quotes = Quote.objects.filter(status=status_filter)
    else:
        quotes = Quote.objects.all()

    # ✅ Count for filter buttons
    new_count = Quote.objects.filter(status="new").count()
    pending_count = Quote.objects.filter(status="pending").count()
    active_count = Quote.objects.filter(status="active").count()
    completed_count = Quote.objects.filter(status="completed").count()

    return render(
        request,
        "adminPages/adminquotes.html",
        {
            "quotes": quotes,
            "form": QuoteForm(),
            "quote": quote,
            "new_count": new_count,
            "pending_count": pending_count,
            "active_count": active_count,
            "completed_count": completed_count,
            "total_count": Quote.objects.count(),
        },
    )


@csrf_protect
@login_required
def mark_quote_active(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    # Update the quote status
    quote.status = "active"
    quote.save()

    # 🆕 Automatically create an order if it doesn't exist
    existing_order = Order.objects.filter(customer=quote).first()
    if not existing_order:
        Order.objects.create(
            customer=quote,
            status="pending",
            date=timezone.now(),
            amount=0  # You can update this later
        )

    messages.success(request, f"Quote from {quote.name} marked as active and order created.")
    return redirect("adminquotes")


@csrf_protect
@login_required
def mark_quote_completed(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    try:
        # Get the associated Order
        order = Order.objects.get(customer=quote)
        order.status = "completed"
        order.save()
        messages.success(request, f"Order for {quote.name} marked as completed.")
    except Order.DoesNotExist:
        messages.error(request, f"No order found for quote from {quote.name}.")

    return redirect("adminquotes")


@staff_member_required
@csrf_protect
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.method == "POST":
        message.delete()
        messages.success(request, "✅ Message deleted successfully ✅")
        return redirect("admininbox")  # ✅ This name must match the one in your urls.py


@staff_member_required
def delete_lead(request, lead_id):
    """
    Deletes a lead by its ID.
    """
    try:
        # Fetch the lead or raise a 404 error if it doesn't exist
        lead = get_object_or_404(Lead, id=lead_id)
        lead.delete()  # Delete the lead
        messages.success(request, "Lead deleted successfully!")
    except Exception as e:
        # Handle any exceptions (e.g., lead not found or database errors)
        messages.error(request, f"Error: {str(e)}")

    # Redirect back to admin leads page
    return redirect("adminleads")


@login_required
@csrf_protect
def delete_quote(request, quote_id):
    """
    Deletes a specific quote by ID.
    """
    if request.method == "POST":
        try:
            quote = get_object_or_404(Quote, id=quote_id)
            quote.delete()
            messages.success(request, "Quote deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting quote: {e}")
        return redirect("adminquotes")

@login_required
def send_email(request):
    """Send emails from the /useradmin/ dashboard with a confirmation message."""
    if request.method == "POST":
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if email and subject and message:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,  # Set to False to see errors
                )
                messages.success(request, f"✅ Email sent successfully to {email}!")
            except Exception as e:
                messages.error(request, f"❌ Error sending email: {str(e)}")
        else:
            messages.error(request, "❌ All fields are required!")

        return redirect("useradmin")  # Redirect back to the dashboard

    return render(request, "adminPages/adminhome.html")  # Ensure the correct template is used


@login_required
def update_profile_picture(request):
    user = request.user

    # ✅ Create profile if missing
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('/useradmin/')
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, 'employeePages/update_profile_picture.html', {'form': form})


def custom_password_reset_done(request):
    return render(request, "registration/password_reset_done.html")


def user_login_redirect(request):
    if request.user.is_superuser:
        return redirect('/admin/')  # Redirect SuperAdmin to Django Admin
    elif request.user.is_staff:
        return redirect('/useradmin/')  # Redirect Admin to custom Admin page
    else:
        return redirect('/employee_dashboard/')  # Redirect ediomi12 to employee dashboard
    
    # Logout View
def logout_view(request):
    """Logs the user out and prevents back navigation."""
    logout(request)
    response = redirect("home")  # Redirect to home page
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@csrf_protect
@login_required
def send_email_to_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        from_email = settings.DEFAULT_FROM_EMAIL

        if subject and message:
            send_mail(subject, message, from_email, [lead.email])
            messages.success(request, f"Email sent to {lead.email}.")
            return redirect("adminleads")
        else:
            messages.error(request, "Subject and message are required.")

    return render(request, "adminPages/send_email_form.html", {"lead": lead})

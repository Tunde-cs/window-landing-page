from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from app.models import Lead, Message, Order, Project, Quote, UserCreateForm
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


# Base Views
def BASE(request):
    return render(request, "base/base.html")


def ADMINBASE(request):
    return render(request, "base/adminbase.html")


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
    """Redirects Admins to Admin Dashboard & Employees to Employee Dashboard"""

    user = request.user  # ✅ Define user first

    if user.is_superuser:  
        return admin_dashboard(request)  # ✅ Send Admins to Admin Dashboard

    elif user.groups.filter(name="Employees").exists():
        return employee_dashboard(request)  # ✅ Send Employees to Employee Dashboard

    else:
        return redirect("login")  # 🚨 Unauthorized users redirected


def admin_dashboard(request):
    """Admin Dashboard View - Displays key metrics, recent leads, and sales data."""
    
    user = request.user
    context = {
        "user": user,
        "request": request,
        "unread_messages": 3,  # Example value
    }
    
    try:
        # ✅ Fetch admin-related data
        new_leads_count = Lead.objects.filter(status="new").count()
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

        # ✅ Conversion Rate Fix
        total_leads = Lead.objects.count()
        conversion_rate = round((sales_completed / total_leads) * 100, 2) if total_leads > 0 else 0

        # ✅ Fetch Sales Data for ALL 12 Months
        raw_sales_data = (
            Order.objects.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        # ✅ Ensure ALL 12 Months are Present
        sales_data_dict = {data["month"]: float(data["total"]) for data in raw_sales_data if data["month"]}

        # ✅ Create Full 12-Month Structure
        sales_chart_labels = []
        sales_chart_data = []

        for month in range(1, 13):  # Loop through all 12 months
            sales_chart_labels.append(month_name[month])  # Convert number to month name
            sales_chart_data.append(sales_data_dict.get(month, 0))  # Get sales or default to 0

        # ✅ Convert Data to JSON for Frontend
        sales_chart_labels_json = json.dumps(sales_chart_labels)
        sales_chart_data_json = json.dumps(sales_chart_data)

        # ✅ Pass Data to Frontend
        context.update({
            "metrics": {
                "new_leads_count": new_leads_count,
                "pending_orders_count": pending_orders_count,
                "completed_projects_count": completed_projects_count,
                "monthly_revenue": monthly_revenue,
                "total_quotes": total_quotes,
                "orders_in_progress": orders_in_progress,
                "sales_completed": sales_completed,
                "conversion_rate": conversion_rate,
                "message_count": message_count,
            },
            "sales_chart_labels": sales_chart_labels_json,
            "sales_chart_data": sales_chart_data_json,
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
        })

    return TemplateResponse(request, "adminPages/adminhome.html", context)  # ✅ Ensures proper context handling


def employee_dashboard(request):
    """Employee Dashboard View - Uses same metrics as Admin Dashboard"""
    
    user = request.user
    context = {
        "user": user,
        "request": request,
    }

    try:
        # ✅ Fetch Employee Metrics (Same as Admin)
        new_leads_count = Lead.objects.filter(status="new").count()
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

        # ✅ Conversion Rate Fix
        total_leads = Lead.objects.count()
        conversion_rate = round((sales_completed / total_leads) * 100, 2) if total_leads > 0 else 0

        # ✅ Fetch Sales Data for Charts
        raw_sales_data = (
            Order.objects.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        sales_data_dict = {data["month"]: float(data["total"]) for data in raw_sales_data if data["month"]}

        sales_chart_labels = []
        sales_chart_data = []

        for month in range(1, 13):  # Loop through all 12 months
            sales_chart_labels.append(month_name[month])  # Convert number to month name
            sales_chart_data.append(sales_data_dict.get(month, 0))  # Get sales or default to 0

        # ✅ Convert Data to JSON for Frontend
        sales_chart_labels_json = json.dumps(sales_chart_labels)
        sales_chart_data_json = json.dumps(sales_chart_data)

        # ✅ Pass Employee Data to Template
        context.update({
            "metrics": {
                "new_leads_count": new_leads_count,
                "pending_orders_count": pending_orders_count,
                "completed_projects_count": completed_projects_count,
                "monthly_revenue": monthly_revenue,
                "total_quotes": total_quotes,
                "orders_in_progress": orders_in_progress,
                "sales_completed": sales_completed,
                "conversion_rate": conversion_rate,
                "message_count": message_count,
            },
            "sales_chart_labels": sales_chart_labels_json,
            "sales_chart_data": sales_chart_data_json,
        })

    except Exception as e:
        print(f"Error fetching data: {e}")
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
        })

    return render(request, "employeePages/employee_dashboard.html", context)


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


def view_order(request, id):
    # Fetch the order with the given id, or return a 404 if not found
    order = get_object_or_404(Order, id=id)

    # Return the order details page
    return render(request, "adminPages/order_details.html", {"order": order})


def projects_view(request):
    projects = Project.objects.all()
    return render(request, "adminPages/adminprojects.html", {"projects": projects})


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


# Admin Inbox View
@staff_member_required
def admin_inbox(request):
    messages = Message.objects.order_by("-created_at")  # Ordered messages
    leads = Lead.objects.order_by("-created_at")  # Ordered leads

    # ✅ Debugging
    print("Total Messages:", messages.count())
    print("Total Leads:", leads.count())

    context = {
        "messages": messages,
        "leads": leads,
        "message_count": messages.count(),  # Total messages
        "lead_count": leads.count(),  # Total leads
    }
    return render(request, "adminPages/admininbox.html", context)


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
    """
    Handles lead submissions for admin users.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name", "Anonymous")  # Default to 'Anonymous'
        phone = request.POST.get("phone", "")

        # Validate email
        if not email:
            messages.error(request, "Email is required.")
            return redirect("adminleads")

        # Validate phone number
        if phone and not re.match(r"^\+?\d{9,15}$", phone):
            messages.error(request, "Invalid phone number format.")
            return redirect("adminleads")

        # Check for duplicate email
        if Lead.objects.filter(email=email).exists():
            messages.error(request, "This email has already been submitted.")
        else:
            try:
                # Save the lead to the database
                Lead.objects.create(name=name, email=email, phone=phone)
                messages.success(request, "Lead submitted successfully!")
            except Exception as e:
                print(f"Error saving lead: {str(e)}")
                messages.error(
                    request,
                    "An error occurred while saving the lead. Please try again.",
                )

        # Redirect back to the admin leads page
        return redirect("adminleads")

    # Render the admin leads page with all leads
    leads = Lead.objects.all().order_by("-created_at")
    return render(request, "adminPages/adminleads.html", {"leads": leads})


@csrf_protect
def admin_quotes_view(request, quote_id=None):
    if request.method == "POST":
        # Handle form submission
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote added successfully!")
        else:
            messages.error(request, "Error adding quote. Please check the form.")

    if quote_id:
        # Show details for a specific quote
        quote = get_object_or_404(Quote, id=quote_id)
        return render(request, "adminPages/adminquotes.html", {"quote": quote})

    # List all quotes
    quotes = Quote.objects.all()
    return render(
        request, "adminPages/adminquotes.html", {"quotes": quotes, "form": QuoteForm()}
    )


def edit_order(request, id):
    """
    View to edit an existing order.
    """
    # Fetch the order by its ID or return a 404 if not found
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        # Get updated status from form data
        new_status = request.POST.get("status")
        if new_status:
            order.status = new_status  # Update order status
        # Update additional fields if needed
        order.save()

        messages.success(request, f"Order {order.id} updated successfully!")
        
        # Redirect back to order details page
        return redirect(reverse("view_order", kwargs={"id": order.id}))

    # Pass order data to template
    return render(request, "adminPages/edit_order.html", {"order": order})

@login_required
@csrf_protect
def delete_message(request, message_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this message.")
        return redirect("inbox")

    message = get_object_or_404(Message, id=message_id)
    message.delete()
    messages.success(request, "Message deleted successfully.")
    return redirect("inbox")


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


@staff_member_required
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



import requests
from django.core.mail import send_mail
from django.conf import settings

# ✅ Load Page ID and Token from settings
PAGE_ID = settings.FB_PAGE_ID
access_token = settings.FB_PAGE_ACCESS_TOKEN

def fetch_facebook_lead(leadgen_id):
    url = f"https://graph.facebook.com/v19.0/{leadgen_id}?access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Failed to fetch lead:", response.status_code, response.text)
        return None

def send_facebook_lead_email(full_name, email, phone):
    try:
        send_mail(
            subject=f"📩 New Facebook Lead: {full_name}",
            message=f"Name: {full_name}\nEmail: {email}\nPhone: {phone}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SALES_EMAIL],
            fail_silently=False,
        )
        print("✅ Facebook lead email sent.")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

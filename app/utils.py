import requests
from django.core.mail import send_mail
from django.conf import settings


# Known Page ID – confirmed working
PAGE_ID = '673177245868522'

# Your current valid USER token (used for API requests)
access_token = 'EAAJas8i3ZCq8BO2rhHE2tnz5kdFzt7aTEhjhdZAP44NK1ctOCj0E6PPKye03D5ZB97CmMePUOyZASDfDbNhUZCDUuSc3QWD005A5nNOPZCHKcBpQtZASb6RRIAVBPT9MAArIQFrh1j1Fj2cq7iJLyApZCMR3h9ACr3ny5sD3mY39erBD2utszCj7cVf3CC8PFci22AvE9xuDYwyZBX4J1uNYZD'

# Fetch Facebook lead using leadgen_id and your valid token
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
            recipient_list=[settings.SALES_EMAIL],  # ✅ use SALES_EMAIL instead
            fail_silently=False,
        )
        print("✅ Facebook lead email sent.")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

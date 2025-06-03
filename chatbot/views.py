from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import os
import json
import logging
from app.models import Message  
import re
from app.models import ChatbotLead
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv


load_dotenv()

# ✅ Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt  # ✅ Disable CSRF for API
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "❗ Please enter a message. 😊"}, status=400)

            # ✅ 🔽 Save message to the Message model
            Message.objects.create(
                sender="Chatbot User",
                subject="Chatbot Inquiry",
                content=user_message,
                is_read=False
            )

            # ✅ Generate AI response using GPT-3.5-Turbo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly and engaging AI assistant for Window Genius AI, a window replacement company. "
                            "Your job is to collect the customer's name, email, and phone number in a natural conversation. "
                            "Ask for them one at a time: start with name, then email, then phone, then zip code. "
                            "Then ask how you can assist (quote, consultation, or question). "
                            "Be conversational and warm. Use emojis 🎉🏡🔧💡 to make responses friendly and engaging. "
                            "Once you have all the info, confirm the details and let them know someone will reach out soon."

                        )
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
            )
            chatbot_reply = response["choices"][0]["message"]["content"].strip()

            # ✅ Try to capture lead info from message (if any)
            if "@" in user_message:
                try:
                    name_match = re.search(r"name[:\-]?\s*([a-zA-Z ]+)", user_message, re.IGNORECASE)
                    email_match = re.search(r"[\w\.-]+@[\w\.-]+", user_message)
                    phone_match = re.search(r"\b\d{10,}\b", user_message)

                    name = name_match.group(1).strip() if name_match else "Anonymous"
                    email = email_match.group(0) if email_match else None
                    phone = phone_match.group(0) if phone_match else None

                    if email:
                        ChatbotLead.objects.create(name=name, email=email, phone=phone)
                        

                        # ✅ Send alert email to sales only (loaded from .env)
                        from_email = os.environ.get("DEFAULT_FROM_EMAIL")
                        sales_email = os.environ.get("EMAIL_HOST_USER")  # Same as DEFAULT_FROM_EMAIL in your case

                        send_mail(
                            subject="🚀 New Chatbot Lead Captured",
                            message=f"Name: {name}\nEmail: {email}\nPhone: {phone or 'N/A'}",
                            from_email=from_email,
                            recipient_list=[sales_email],
                            fail_silently=True
                        )
                except Exception as e:
                    print(f"❌ Lead parsing failed: {e}")

            # ✅ Add CORS headers
            response_data = JsonResponse({"reply": chatbot_reply})
            response_data["Access-Control-Allow-Origin"] = "*"
            response_data["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response_data["Access-Control-Allow-Headers"] = "Content-Type"
            return response_data

        except Exception as e:
            return JsonResponse({"reply": f"⚠️ Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. ❌"}, status=405)

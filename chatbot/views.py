from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, uuid, os
from chatbot.models import Conversation
from app.models import ChatbotLead
import openai
from django.core.mail import send_mail
from django.conf import settings

# ✅ Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method ❌"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "❗ Please enter a message. 😊"}, status=400)

        # ✅ Ensure the session exists so user_id stays consistent
        if not request.session.session_key:
            request.session.create()

        user_id = request.session.session_key
        convo, _ = Conversation.objects.get_or_create(user_id=user_id)

        # 🔎 Debug print
        print(f"✅ Chat step: {convo.step} | Message: {user_message}")

        bot_reply = ""

        # 🔹 Step 1: Intro
        if convo.step == "intro":
            convo.step = "name"
            convo.save()
            bot_reply = "👋 Hi there! I’m Window Genius AI. What’s your full name?"

        # 🔹 Step 2: Name
        elif convo.step == "name":
            clean_name = user_message.strip()
            if clean_name.lower() in ["hi", "hello", "hey"]:
                return JsonResponse({"reply": "No worries 😊, could you tell me your full name?"})

            for prefix in ["my name is", "i am", "i'm"]:
                if clean_name.lower().startswith(prefix):
                    clean_name = clean_name[len(prefix):].strip()

            convo.name = clean_name
            convo.step = "email"
            convo.save()
            bot_reply = f"Thanks {convo.name}! ✨ What’s your email?"

        # 🔹 Step 3: Email
        elif convo.step == "email":
            clean_email = user_message.strip()
            if "@" not in clean_email or "." not in clean_email:
                return JsonResponse({"reply": "Hmm 🤔 that doesn’t look like an email. Could you type it again?"})

            convo.email = clean_email
            convo.step = "phone"
            convo.save()
            bot_reply = "Got it 📧. What’s your phone number?"

        # 🔹 Step 4: Phone
        elif convo.step == "phone":
            clean_phone = user_message.strip()
            if not clean_phone.replace("+", "").replace("-", "").isdigit() or len(clean_phone) < 7:
                return JsonResponse({"reply": "That doesn’t look like a valid phone number ☎️. Please try again."})

            convo.phone = clean_phone
            convo.step = "zipcode"
            convo.save()
            bot_reply = "Perfect! 📱 What’s your ZIP code?"

        # 🔹 Step 5: Zipcode
        elif convo.step == "zipcode":
            clean_zip = user_message.strip()
            if not clean_zip.isdigit():
                return JsonResponse({"reply": "Please enter a valid numeric ZIP code 📍."})

            convo.zipcode = clean_zip
            convo.step = "service"
            convo.save()
            bot_reply = "Almost done 🙌. What service are you interested in (quote, consultation, or question)?"

        # 🔹 Step 6: Service
        elif convo.step == "service":
            convo.service = user_message.strip()
            convo.step = "done"
            convo.save()

            # ✅ Save final lead
            ChatbotLead.objects.create(
                name=convo.name,
                email=convo.email,
                phone=convo.phone,
                service=convo.service,
            )

            # ✅ Send notification email
            try:
                send_mail(
                    subject="🚀 New Chatbot Lead Captured",
                    message=(
                        f"Name: {convo.name}\n"
                        f"Email: {convo.email}\n"
                        f"Phone: {convo.phone}\n"
                        f"Zip: {convo.zipcode}\n"
                        f"Service: {convo.service}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"❌ Email send failed: {e}")

            bot_reply = (
                f"✅ Thanks {convo.name}! We’ve saved your details 🎉. "
                "Our team will reach out soon to help with your request 🏡."
            )

        # 🔹 Step 7: Done
        else:
            bot_reply = "I’ve got all your details ✅. Someone from our team will be in touch soon!"

        # 🔹 Optional GPT polish (only for final replies, not validation prompts)
        if convo.step == "done":
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Polish this chatbot response to sound warm, friendly, and professional with emojis."},
                        {"role": "user", "content": bot_reply},
                    ],
                    max_tokens=100,
                )
                bot_reply = response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"⚠️ GPT polish failed: {e}")

        return JsonResponse({"reply": bot_reply})

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return JsonResponse({"reply": f"⚠️ Error: {str(e)}"}, status=500)

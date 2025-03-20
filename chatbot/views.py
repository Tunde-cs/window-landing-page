from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import os
import json
import logging
from dotenv import load_dotenv


# ✅ Load OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt  # ✅ Disable CSRF for chatbot API
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "Please enter a message."}, status=400)

            # ✅ Generate AI response using GPT-3.5-Turbo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # ✅ Use latest OpenAI model
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI assistant for OUR window replacement company. "
                            "You help customers with window sales, repairs, and installation inquiries. "
                            "Always promote OUR company’s services and do not refer them to other companies. "
                            "Encourage customers to schedule a consultation and fill out the form above for a quote."
                        )
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
            )
            chatbot_reply = response["choices"][0]["message"]["content"].strip()

            return JsonResponse({"reply": chatbot_reply})

        except Exception as e:
            return JsonResponse({"reply": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def chat(request):
    response = JsonResponse({"reply": "Hello!"})
    response["Access-Control-Allow-Origin"] = "*"  # Allow all origins
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response
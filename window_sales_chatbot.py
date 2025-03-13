from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import logging


# Load environment variables from .env
load_dotenv()

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize Flask app
app = Flask(__name__)
CORS(app)

# ✅ Store user session data
session_data = {}

# ✅ Available Window Types
WINDOW_TYPES = ["Single Hung", "Double Hung", "Casement Window", "Sliding Window", "Picture Window"]

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip().lower()
    user_id = request.remote_addr  # Identify users by IP (or session system)

    # ✅ Initialize user session if new
    if user_id not in session_data:
        session_data[user_id] = {
            "last_request": None,
            "name": None,
            "phone": None,
            "email": None,
            "consultation_time": None,
            "interested_window": None
        }
        return jsonify({"reply": "Hello! I'm your Window Sales Assistant. How can I help you today?"})

    # ✅ Check if user is requesting information about windows
    if "window" in user_message or "type" in user_message:
        response = "We offer the following window types: " + ", ".join(WINDOW_TYPES) + ". Which one interests you?"

    # ✅ Detect window selection
    elif any(window.lower() in user_message for window in WINDOW_TYPES):
        session_data[user_id]["interested_window"] = user_message
        response = f"Great choice! How many {user_message.title()} windows do you need?"

    # ✅ Detect quantity input
    elif user_message.isdigit():
        if session_data[user_id]["interested_window"]:
            session_data[user_id]["quantity"] = user_message
            response = f"Noted! Would you like to schedule a free consultation to discuss pricing and installation?"
        else:
            response = "Could you specify which window type you're interested in first?"

    # ✅ If user requests a consultation
    elif "consultation" in user_message or "yes" in user_message:
        session_data[user_id]["last_request"] = "consultation"
        response = "I'd be happy to set up a consultation! Can I have your name?"

    # ✅ Collect name
    elif session_data[user_id]["last_request"] == "consultation" and session_data[user_id]["name"] is None:
        session_data[user_id]["name"] = user_message.title()
        response = f"Thanks, {session_data[user_id]['name']}! Can I get your phone number?"

    # ✅ Collect phone number
    elif session_data[user_id]["name"] and session_data[user_id]["phone"] is None:
        if user_message.replace(" ", "").isdigit():
            session_data[user_id]["phone"] = user_message
            response = "Got it! Lastly, can I have your email address?"
        else:
            response = "Please enter a valid phone number."

    # ✅ Collect email
    elif session_data[user_id]["phone"] and session_data[user_id]["email"] is None:
        if "@" in user_message and "." in user_message:
            session_data[user_id]["email"] = user_message
            response = "Thank you! What date and time work best for your consultation?"
        else:
            response = "Please enter a valid email address."

    # ✅ Collect preferred consultation time
    elif session_data[user_id]["email"] and session_data[user_id]["consultation_time"] is None:
        session_data[user_id]["consultation_time"] = user_message
        response = f"Perfect! We have scheduled your consultation for {user_message}. Our team will contact you soon. Thank you!"

    # ✅ If user asks general questions, educate but redirect
    elif "how" in user_message or "what" in user_message or "difference" in user_message:
        response = "Great question! Our windows vary based on design, efficiency, and installation type. Would you like a consultation to learn more?"

    # ✅ Default response for unhandled cases
    else:
        response = "I'm happy to help! Are you looking for information on window options or scheduling a consultation?"

    return jsonify({"reply": response})


if __name__ == "__main__":
    app.run(debug=True)

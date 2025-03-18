import openai
import os

# Load OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chat_response(prompt):
    """
    Sends a user prompt to OpenAI and returns the chatbot response.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change this to match your OpenAI model
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

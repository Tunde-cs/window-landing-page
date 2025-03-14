from django.urls import path
from .views import chat  # Import chat function from views

urlpatterns = [
    path("chat/", chat, name="chatbot"),  # API endpoint: /api/chat/
]

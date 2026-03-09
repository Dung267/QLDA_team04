# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_chatbot, name='ask_chatbot'),  # Gửi câu hỏi cho chatbot
    path('history/', views.chat_history, name='chat_history'),  # Lịch sử trò chuyện
]
from django.urls import path
from . import api_views

urlpatterns = [
    path('chat/', api_views.chat_message_api, name='api_chat'),
    path('faqs/', api_views.FAQListAPIView.as_view(), name='api_faq_list'),
    path('stats/', api_views.chatbot_stats_api, name='api_chatbot_stats'),
]

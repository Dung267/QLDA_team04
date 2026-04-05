from django.urls import path
from . import views
app_name = 'chatbot'
urlpatterns = [
    path('', views.chatbot_page, name='chat'),
    path('api/', views.chat_api, name='api'),
    path('questions/', views.popular_questions, name='questions'),
    path('stats/', views.chat_stats, name='stats'),
]

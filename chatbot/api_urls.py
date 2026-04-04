from django.urls import path
from . import views
urlpatterns = [
    path('chat/', views.chat_api, name='api_chat'),
    path('questions/', views.popular_questions, name='api_questions'),
]

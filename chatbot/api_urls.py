from django.urls import path
from .views import chat_api, rate_session

urlpatterns = [
    path('chat/', chat_api, name='chatbot_api'),
    path('rate/<str:session_id>/', rate_session, name='rate_session'),
]

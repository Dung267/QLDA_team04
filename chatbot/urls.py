from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_widget, name='widget'),
    path('api/chat/', views.chat_api, name='api'),
    path('api/rate/<str:session_id>/', views.rate_session, name='rate'),
    path('faq/', views.faq_list, name='faq'),
    path('stats/', views.chatbot_stats, name='stats'),
]

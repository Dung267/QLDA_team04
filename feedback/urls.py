from django.urls import path
from . import views
app_name = 'feedback'
urlpatterns = [
    path('', views.feedback_list, name='list'),
    path('create/', views.FeedbackCreateView.as_view(), name='create'),
    path('<int:pk>/', views.feedback_detail, name='detail'),
    path('<int:pk>/like/', views.feedback_like, name='like'),
    path('<int:pk>/reply/', views.feedback_reply, name='reply'),
    path('<int:pk>/important/', views.toggle_important, name='important'),
    path('<int:pk>/hide/', views.hide_feedback, name='hide'),
    path('stats/', views.feedback_stats, name='stats'),
]

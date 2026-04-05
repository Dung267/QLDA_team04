from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.FeedbackListAPIView.as_view(), name='api_feedback_list'),
    path('<int:pk>/', api_views.FeedbackDetailAPIView.as_view(), name='api_feedback_detail'),
    path('<int:pk>/like/', api_views.like_feedback_api, name='api_feedback_like'),
    path('stats/', api_views.feedback_stats_api, name='api_feedback_stats'),
]

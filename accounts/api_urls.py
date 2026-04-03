from django.urls import path
from . import api_views

urlpatterns = [
    path('users/', api_views.UserListAPIView.as_view(), name='api_user_list'),
    path('users/<int:pk>/', api_views.UserDetailAPIView.as_view(), name='api_user_detail'),
]
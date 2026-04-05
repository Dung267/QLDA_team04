from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.NotificationListAPIView.as_view(), name='api_notification_list'),
    path('<int:pk>/read/', api_views.mark_read_api, name='api_notification_read'),
    path('read-all/', api_views.mark_all_read_api, name='api_notification_read_all'),
    path('unread-count/', api_views.unread_count_api, name='api_notification_count'),
]

from django.urls import path
from . import views

app_name = 'flood'

urlpatterns = [
    # Danh sách & tạo mới
    path('', views.alert_list, name='alert_list'),
    path('create/', views.alert_create, name='alert_create'),

    # Chi tiết & chỉnh sửa
    path('<int:pk>/', views.alert_detail, name='alert_detail'),
    path('<int:pk>/edit/', views.alert_edit, name='alert_edit'),

    # Hành động
    path('<int:pk>/resolve/', views.alert_resolve, name='alert_resolve'),
    path('<int:pk>/send-sms/', views.alert_send_sms, name='send_sms'),
    path('<int:pk>/notify-rescue/', views.alert_notify_rescue, name='notify_rescue'),
    path('<int:pk>/add-update/', views.alert_add_update, name='add_update'),

    # API (dùng cho bản đồ / WebSocket client)
    path('api/active/', views.active_alerts_api, name='active_api'),
]
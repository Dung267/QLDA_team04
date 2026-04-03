from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('create/', views.request_create, name='request_create'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/cancel/', views.request_cancel, name='request_cancel'),
    path('<int:pk>/rate/', views.request_rate, name='request_rate'),
    path('<int:pk>/receive/', views.request_receive, name='request_receive'),
    path('<int:pk>/assign/', views.request_assign, name='request_assign'),
    path('<int:pk>/progress/', views.request_update_progress, name='request_progress'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('stats/', views.maintenance_stats, name='stats'),
]
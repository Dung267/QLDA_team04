from django.urls import path
from . import views
app_name = 'permits'
urlpatterns = [
    path('', views.permit_list, name='list'),
    path('create/', views.permit_create, name='create'),
    path('<int:pk>/', views.permit_detail, name='detail'),
    path('<int:pk>/submit/', views.permit_submit, name='submit'),
    path('<int:pk>/process/', views.permit_process, name='process'),
    path('stats/', views.permit_stats, name='stats'),
]

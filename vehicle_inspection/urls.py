from django.urls import path
from . import views
app_name = 'vehicle_inspection'
urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('', views.inspection_list, name='inspection_list'),
    path('schedule/', views.schedule_inspection, name='schedule'),
    path('<int:pk>/cancel/', views.cancel_inspection, name='cancel'),
    path('<int:pk>/update/', views.update_inspection, name='update'),
    path('<int:pk>/pay/', views.pay_fee, name='pay'),
]

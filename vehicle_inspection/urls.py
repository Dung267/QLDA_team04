from django.urls import path
from . import views
app_name = 'vehicle_inspection'
urlpatterns = [
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/add/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('', views.InspectionListView.as_view(), name='inspection_list'),
    path('schedule/', views.ScheduleCreateView.as_view(), name='schedule'),
    path('<int:pk>/cancel/', views.cancel_inspection, name='cancel'),
    path('<int:pk>/update/', views.update_inspection, name='update'),
    path('<int:pk>/pay/', views.pay_fee, name='pay'),
]

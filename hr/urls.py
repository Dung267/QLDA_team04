from django.urls import path
from . import views
app_name = 'hr'
urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('leave/', views.leave_list, name='leave_list'),
    path('leave/create/', views.leave_create, name='leave_create'),
    path('trainings/', views.training_list, name='training_list'),
]

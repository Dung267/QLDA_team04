from django.urls import path
from . import api_views

urlpatterns = [
    path('employees/', api_views.EmployeeListAPIView.as_view(), name='api_employee_list'),
    path('employees/<int:pk>/', api_views.EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
    path('assignments/', api_views.WorkAssignmentListAPIView.as_view(), name='api_assignment_list'),
    path('leave/', api_views.LeaveRequestListAPIView.as_view(), name='api_leave_list'),
    path('leave/<int:pk>/approve/', api_views.approve_leave_api, name='api_leave_approve'),
    path('departments/', api_views.DepartmentListAPIView.as_view(), name='api_department_list'),
]

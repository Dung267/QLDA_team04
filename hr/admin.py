from django.contrib import admin
from .models import Department, Employee, WorkAssignment, LeaveRequest, Training

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name','code','manager']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user','employee_id','department','position','is_active']
    list_filter = ['department','is_active']
    search_fields = ['user__username','user__first_name','employee_id']

@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ['title','employee','status','due_date']
    list_filter = ['status']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee','leave_type','start_date','end_date','status']
    list_filter = ['status','leave_type']

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['title','trainer','start_date','end_date']
    filter_horizontal = ['participants']

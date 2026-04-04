from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Employee, WorkAssignment, LeaveRequest, Training, Department
from accounts.decorators import staff_required

@login_required
@staff_required
def employee_list(request):
    employees = Employee.objects.select_related('user','department').filter(is_active=True)
    paginator = Paginator(employees, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'hr/employee_list.html',{'page_obj':page,'page_title':'Nhân sự'})

@login_required
@staff_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    assignments = emp.assignments.all()[:10]
    return render(request,'hr/employee_detail.html',{'emp':emp,'assignments':assignments,'page_title':str(emp)})

@login_required
@staff_required
def assignment_list(request):
    assignments = WorkAssignment.objects.select_related('employee','assigned_by').all()
    paginator = Paginator(assignments, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'hr/assignment_list.html',{'page_obj':page,'page_title':'Phân công công việc'})

@login_required
@staff_required
def assignment_create(request):
    from .forms import WorkAssignmentForm
    if request.method=='POST':
        form = WorkAssignmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.assigned_by = request.user
            a.save()
            messages.success(request,'Đã tạo phân công.')
            return redirect('hr:assignment_list')
    else:
        form = WorkAssignmentForm()
    return render(request,'hr/assignment_form.html',{'form':form,'page_title':'Tạo phân công'})

@login_required
def leave_list(request):
    if hasattr(request.user,'employee_profile'):
        leaves = request.user.employee_profile.leave_requests.all()
    else:
        leaves = LeaveRequest.objects.none()
    paginator = Paginator(leaves, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'hr/leave_list.html',{'page_obj':page,'page_title':'Đơn nghỉ phép'})

@login_required
def leave_create(request):
    from .forms import LeaveRequestForm
    if not hasattr(request.user,'employee_profile'):
        messages.error(request,'Bạn không có hồ sơ nhân viên.')
        return redirect('dashboard')
    if request.method=='POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            lr = form.save(commit=False)
            lr.employee = request.user.employee_profile
            lr.save()
            messages.success(request,'Đã gửi đơn nghỉ phép.')
            return redirect('hr:leave_list')
    else:
        form = LeaveRequestForm()
    return render(request,'hr/leave_form.html',{'form':form,'page_title':'Xin nghỉ phép'})

@login_required
@staff_required
def training_list(request):
    trainings = Training.objects.all()
    return render(request,'hr/training_list.html',{'trainings':trainings,'page_title':'Đào tạo'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Employee, WorkAssignment, LeaveRequest, Meeting, Department
from accounts.decorators import staff_required


@login_required
@staff_required
def employee_list(request):
    employees = Employee.objects.select_related('user', 'department').all()
    paginator = Paginator(employees, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'hr/employee_list.html', {'page_obj': page, 'page_title': 'Nhân sự'})


@login_required
@staff_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    assignments = WorkAssignment.objects.filter(assigned_to=emp.user).order_by('-created_at')[:10]
    return render(request, 'hr/employee_detail.html', {'emp': emp, 'assignments': assignments})


@login_required
def assignment_list(request):
    if request.user.role == 'citizen':
        return redirect('dashboard')
    assignments = WorkAssignment.objects.select_related('assigned_to', 'assigned_by')
    if request.user.role not in ('admin', 'manager'):
        assignments = assignments.filter(assigned_to=request.user)
    paginator = Paginator(assignments, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'hr/assignment_list.html', {'page_obj': page, 'page_title': 'Công việc'})


@login_required
@staff_required
def assignment_create(request):
    from .forms import WorkAssignmentForm
    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_by = request.user
            assignment.save()
            messages.success(request, 'Đã tạo công việc.')
            return redirect('hr:assignment_list')
    else:
        form = WorkAssignmentForm()
    return render(request, 'hr/assignment_form.html', {'form': form, 'page_title': 'Tạo công việc'})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(WorkAssignment, pk=pk)
    return render(request, 'hr/assignment_detail.html', {'assignment': assignment})


@login_required
def leave_request_list(request):
    leaves = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    if request.user.role in ('admin', 'manager'):
        leaves = LeaveRequest.objects.all().order_by('-created_at')
    paginator = Paginator(leaves, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'hr/leave_list.html', {'page_obj': page, 'page_title': 'Nghỉ phép'})


@login_required
def leave_request_create(request):
    from .forms import LeaveRequestForm
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            messages.success(request, 'Đã gửi yêu cầu nghỉ phép.')
            return redirect('hr:leave_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'hr/leave_form.html', {'form': form, 'page_title': 'Xin nghỉ phép'})


@login_required
@staff_required
def leave_approve(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave.status = 'approved'
            leave.approved_by = request.user
        else:
            leave.status = 'rejected'
            leave.rejection_reason = request.POST.get('reason', '')
        leave.save()
        messages.success(request, f'Đã {"chấp thuận" if action == "approve" else "từ chối"} yêu cầu nghỉ phép.')
    return redirect('hr:leave_list')


@login_required
def meeting_list(request):
    meetings = Meeting.objects.filter(participants=request.user) | Meeting.objects.filter(organizer=request.user)
    meetings = meetings.distinct().order_by('-scheduled_at')
    return render(request, 'hr/meeting_list.html', {'meetings': meetings, 'page_title': 'Lịch họp'})


@login_required
def meeting_create(request):
    from .forms import MeetingForm
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.save()
            form.save_m2m()
            messages.success(request, 'Đã tạo cuộc họp.')
            return redirect('hr:meeting_list')
    else:
        form = MeetingForm()
    return render(request, 'hr/meeting_form.html', {'form': form, 'page_title': 'Tạo cuộc họp'})


@login_required
@staff_required
def hr_report(request):
    from django.db.models import Count
    stats = {
        'total_employees': Employee.objects.filter(employment_status='active').count(),
        'by_department': list(Employee.objects.values('department__name').annotate(c=Count('id'))),
        'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
        'pending_assignments': WorkAssignment.objects.filter(status='pending').count(),
    }
    return render(request, 'hr/report.html', {'stats': stats, 'page_title': 'Báo cáo nhân sự'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import date

from .models import Employee, WorkAssignment, LeaveRequest, Training, Department
from accounts.decorators import staff_required


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_business_days(start, end):
    """Đếm số ngày làm việc (trừ T7, CN) giữa hai ngày."""
    if not start or not end or end < start:
        return 0
    days = 0
    cur = start
    while cur <= end:
        if cur.weekday() < 5:
            days += 1
        cur = date.fromordinal(cur.toordinal() + 1)
    return days


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

@login_required
@staff_required
def employee_list(request):
    qs = Employee.objects.select_related('user', 'department').filter(is_active=True)

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(employee_id__icontains=q) |
            Q(position__icontains=q)
        )

    # Lọc phòng ban
    dept_id = request.GET.get('department', '')
    if dept_id:
        qs = qs.filter(department_id=dept_id)

    departments = Department.objects.all()
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'hr/employee_list.html', {
        'page_obj': page,
        'departments': departments,
        'total_count': Employee.objects.filter(is_active=True).count(),
        'page_title': 'Nhân sự',
    })


@login_required
@staff_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee.objects.select_related('user', 'department'), pk=pk)
    assignments = emp.assignments.select_related('assigned_by').order_by('-created_at')[:10]
    leave_requests = emp.leave_requests.order_by('-created_at')[:5]
    trainings = emp.trainings.order_by('-start_date')[:5]

    # Thống kê công việc
    assignment_stats = {
        'todo': emp.assignments.filter(status='todo').count(),
        'in_progress': emp.assignments.filter(status='in_progress').count(),
        'done': emp.assignments.filter(status='done').count(),
    }

    return render(request, 'hr/employee_detail.html', {
        'emp': emp,
        'assignments': assignments,
        'leave_requests': leave_requests,
        'trainings': trainings,
        'assignment_stats': assignment_stats,
        'page_title': str(emp),
    })


# ---------------------------------------------------------------------------
# Work Assignment
# ---------------------------------------------------------------------------

@login_required
@staff_required
def assignment_list(request):
    qs = WorkAssignment.objects.select_related('employee__user', 'employee__department', 'assigned_by')

    # Filter status
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    # Filter employee
    emp_id = request.GET.get('employee', '')
    if emp_id:
        qs = qs.filter(employee_id=emp_id)

    # Tìm kiếm
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(employee__user__first_name__icontains=q) |
            Q(employee__user__last_name__icontains=q)
        )

    # Thống kê
    stats = {
        'todo': WorkAssignment.objects.filter(status='todo').count(),
        'in_progress': WorkAssignment.objects.filter(status='in_progress').count(),
        'done': WorkAssignment.objects.filter(status='done').count(),
        'cancelled': WorkAssignment.objects.filter(status='cancelled').count(),
    }

    employees = Employee.objects.filter(is_active=True).select_related('user')
    paginator = Paginator(qs.order_by('due_date', '-created_at'), 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'hr/assignment_list.html', {
        'page_obj': page,
        'stats': stats,
        'employees': employees,
        'today': date.today(),
        'page_title': 'Phân công công việc',
    })


@login_required
@staff_required
def assignment_create(request):
    from .forms import WorkAssignmentForm
    # Annotate số task đang làm cho mỗi nhân viên để hiển thị workload
    employee_list = (
        Employee.objects
        .filter(is_active=True)
        .select_related('user', 'department')
        .annotate(active_tasks_count=Count(
            'assignments',
            filter=Q(assignments__status__in=['todo', 'in_progress'])
        ))
    )

    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.assigned_by = request.user
            a.save()
            messages.success(request, 'Đã tạo phân công công việc thành công.')
            return redirect('hr:assignment_list')
    else:
        form = WorkAssignmentForm()
        # Preselect nhân viên nếu có param
        preselected = request.GET.get('employee')

    return render(request, 'hr/assignment_form.html', {
        'form': form,
        'employee_list': employee_list,
        'preselected_employee': request.GET.get('employee'),
        'page_title': 'Giao việc mới',
    })


@login_required
@staff_required
def assignment_edit(request, pk):
    from .forms import WorkAssignmentForm
    assignment = get_object_or_404(WorkAssignment, pk=pk)
    employee_list = (
        Employee.objects
        .filter(is_active=True)
        .select_related('user', 'department')
        .annotate(active_tasks_count=Count(
            'assignments',
            filter=Q(assignments__status__in=['todo', 'in_progress'])
        ))
    )

    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật phân công.')
            return redirect('hr:assignment_list')
    else:
        form = WorkAssignmentForm(instance=assignment)

    return render(request, 'hr/assignment_form.html', {
        'form': form,
        'object': assignment,
        'employee_list': employee_list,
        'page_title': 'Cập nhật công việc',
    })


@login_required
@staff_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(WorkAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Đã xóa phân công.')
    return redirect('hr:assignment_list')


# ---------------------------------------------------------------------------
# Leave Request
# ---------------------------------------------------------------------------

@login_required
def leave_list(request):
    # Staff/admin xem tất cả, nhân viên thường chỉ xem của mình
    is_manager = request.user.is_staff or getattr(request.user, 'is_admin', False) or \
                 getattr(request.user, 'is_staff_member', False)

    if is_manager:
        qs = LeaveRequest.objects.select_related('employee__user', 'approved_by')
    else:
        if not hasattr(request.user, 'employee_profile'):
            return render(request, 'hr/leave_list.html', {
                'page_obj': None,
                'page_title': 'Đơn nghỉ phép',
            })
        qs = request.user.employee_profile.leave_requests.select_related('employee__user', 'approved_by')

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    leave_type_filter = request.GET.get('leave_type', '')
    if leave_type_filter:
        qs = qs.filter(leave_type=leave_type_filter)

    emp_filter = request.GET.get('employee', '')
    if emp_filter and is_manager:
        qs = qs.filter(employee_id=emp_filter)

    month_filter = request.GET.get('month', '')
    if month_filter:
        try:
            yr, mo = month_filter.split('-')
            qs = qs.filter(start_date__year=int(yr), start_date__month=int(mo))
        except (ValueError, AttributeError):
            pass

    # Thêm số ngày cho mỗi đơn
    leave_list_data = list(qs.order_by('-created_at'))
    for leave in leave_list_data:
        leave.num_days = _count_business_days(leave.start_date, leave.end_date)

    # Stats
    today = date.today()
    base_qs = LeaveRequest.objects.all() if is_manager else qs
    pending_count = LeaveRequest.objects.filter(status='pending').count() if is_manager else qs.filter(status='pending').count()
    approved_count = LeaveRequest.objects.filter(status='approved').count() if is_manager else qs.filter(status='approved').count()
    rejected_count = LeaveRequest.objects.filter(status='rejected').count() if is_manager else qs.filter(status='rejected').count()
    # Ngày nghỉ tháng hiện tại (đã duyệt)
    this_month_leaves = LeaveRequest.objects.filter(
        status='approved',
        start_date__year=today.year,
        start_date__month=today.month
    ) if is_manager else qs.filter(
        status='approved',
        start_date__year=today.year,
        start_date__month=today.month
    )
    total_days = sum(_count_business_days(l.start_date, l.end_date) for l in this_month_leaves)

    employee_list_qs = Employee.objects.filter(is_active=True).select_related('user') if is_manager else []

    paginator = Paginator(leave_list_data, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'hr/leave_list.html', {
        'page_obj': page,
        'is_manager': is_manager,
        'employee_list': employee_list_qs,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_days': total_days,
        'today': today,
        'page_title': 'Quản lý nghỉ phép',
    })


@login_required
def leave_create(request):
    from .forms import LeaveRequestForm
    is_manager = request.user.is_staff or getattr(request.user, 'is_admin', False) or \
                 getattr(request.user, 'is_staff_member', False)

    # Nhân viên thường phải có employee_profile
    if not is_manager and not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Bạn không có hồ sơ nhân viên.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            lr = form.save(commit=False)
            if is_manager:
                # Manager chọn nhân viên qua POST param 'employee'
                emp_pk = request.POST.get('employee')
                if emp_pk:
                    lr.employee = get_object_or_404(Employee, pk=emp_pk)
                else:
                    messages.error(request, 'Vui lòng chọn nhân viên.')
                    return redirect('hr:leave_create')
            else:
                lr.employee = request.user.employee_profile
            lr.save()
            messages.success(request, 'Đã gửi đơn nghỉ phép thành công.')
            return redirect('hr:leave_list')
    else:
        form = LeaveRequestForm()

    # Quota phép năm
    annual_used = 0
    if not is_manager and hasattr(request.user, 'employee_profile'):
        annual_used = LeaveRequest.objects.filter(
            employee=request.user.employee_profile,
            leave_type='annual',
            status='approved',
            start_date__year=date.today().year
        ).count()

    employee_list_qs = Employee.objects.filter(is_active=True).select_related('user') if is_manager else []
    preselected = request.GET.get('employee', '')

    return render(request, 'hr/leave_form.html', {
        'form': form,
        'is_manager': is_manager,
        'employee_list': employee_list_qs,
        'preselected': int(preselected) if preselected.isdigit() else None,
        'annual_remaining': max(0, 12 - annual_used),
        'sick_remaining': 5,
        'page_title': 'Xin nghỉ phép',
    })


@login_required
@staff_required
def leave_approve(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.save()
        messages.success(request, f'Đã duyệt đơn nghỉ phép của {leave.employee.user.get_full_name()}.')
    return redirect('hr:leave_list')


@login_required
@staff_required
def leave_reject(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.save()
        messages.warning(request, f'Đã từ chối đơn nghỉ phép của {leave.employee.user.get_full_name()}.')
    return redirect('hr:leave_list')


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

@login_required
@staff_required
def training_list(request):
    today = date.today()
    qs = Training.objects.prefetch_related('participants').annotate(
        participants_count=Count('participants')
    )

    # Filter/search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(trainer__icontains=q))

    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    if year_filter:
        qs = qs.filter(start_date__year=int(year_filter))

    # Thêm computed status vào từng object
    training_list_data = []
    for tr in qs.order_by('-start_date'):
        if tr.start_date > today:
            tr.status = 'upcoming'
        elif tr.end_date < today:
            tr.status = 'completed'
        else:
            tr.status = 'ongoing'
            total = (tr.end_date - tr.start_date).days or 1
            elapsed = (today - tr.start_date).days
            tr.progress_pct = min(100, int(elapsed / total * 100))

        # Dùng title field của model (model dùng 'title', template dùng tr.name)
        tr.name = tr.title
        tr.instructor = tr.trainer
        tr.location = getattr(tr, 'location', '')

        if status_filter and tr.status != status_filter:
            continue
        training_list_data.append(tr)

    # Stats
    all_trainings = Training.objects.all()
    stats = {
        'total': all_trainings.count(),
        'upcoming': sum(1 for t in all_trainings if t.start_date > today),
        'ongoing': sum(1 for t in all_trainings if t.start_date <= today <= t.end_date),
        'completed': sum(1 for t in all_trainings if t.end_date < today),
    }

    year_list = (
        Training.objects.dates('start_date', 'year')
        .values_list('start_date__year', flat=True)
        .distinct().order_by('-start_date__year')
    )

    paginator = Paginator(training_list_data, 12)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'hr/training_list.html', {
        'page_obj': page,
        'stats': stats,
        'year_list': list(year_list),
        'page_title': 'Đào tạo',
    })


@login_required
@staff_required
def training_detail(request, pk):
    training = get_object_or_404(Training.objects.prefetch_related('participants__user'), pk=pk)
    today = date.today()

    if training.start_date > today:
        training.status = 'upcoming'
    elif training.end_date < today:
        training.status = 'completed'
    else:
        training.status = 'ongoing'
        total = (training.end_date - training.start_date).days or 1
        elapsed = (today - training.start_date).days
        training.progress_pct = min(100, int(elapsed / total * 100))

    return render(request, 'hr/training_detail.html', {
        'training': training,
        'page_title': training.title,
    })


@login_required
@staff_required
def training_create(request):
    from .forms import TrainingForm
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo khóa đào tạo thành công.')
            return redirect('hr:training_list')
    else:
        form = TrainingForm()

    return render(request, 'hr/training_form.html', {
        'form': form,
        'page_title': 'Tạo khóa đào tạo',
    })


@login_required
@staff_required
def training_edit(request, pk):
    from .forms import TrainingForm
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật khóa đào tạo.')
            return redirect('hr:training_list')
    else:
        form = TrainingForm(instance=training)

    return render(request, 'hr/training_form.html', {
        'form': form,
        'object': training,
        'page_title': 'Chỉnh sửa khóa đào tạo',
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from .models import MaintenanceRequest, MaintenancePhoto, MaintenanceComment, MaintenanceSchedule
from .forms import MaintenanceRequestForm, MaintenanceCommentForm, MaintenanceScheduleForm
from accounts.decorators import staff_required


@login_required
def request_list(request):
    qs = MaintenanceRequest.objects.select_related('reported_by', 'assigned_to')

    # Người dân chỉ thấy phản ánh của mình
    if request.user.role == 'citizen':
        qs = qs.filter(reported_by=request.user)

    # Filters
    status = request.GET.get('status', '')
    incident_type = request.GET.get('type', '')
    priority = request.GET.get('priority', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    q = request.GET.get('q', '')

    if status:
        qs = qs.filter(status=status)
    if incident_type:
        qs = qs.filter(incident_type=incident_type)
    if priority:
        qs = qs.filter(priority=priority)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(address__icontains=q))

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'maintenance/request_list.html', {
        'page_obj': page,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
        'type_choices': MaintenanceRequest.TYPE_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'page_title': 'Danh sách phản ánh',
    })


@login_required
def request_create(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.reported_by = request.user
            # Kiểm tra trùng
            similar = MaintenanceRequest.objects.filter(
                incident_type=req.incident_type,
                status__in=['pending', 'received', 'assigned', 'in_progress'],
                address__icontains=req.address[:20] if req.address else '',
            ).first()
            if similar:
                req.is_duplicate = True
                req.duplicate_of = similar
            req.save()

            # Upload ảnh/video
            for f in request.FILES.getlist('photos'):
                MaintenancePhoto.objects.create(
                    request=req, image=f, phase='before', uploaded_by=request.user
                )

            messages.success(request, f'Đã gửi phản ánh. Mã theo dõi: #{req.pk}')
            return redirect('maintenance:request_detail', pk=req.pk)
    else:
        form = MaintenanceRequestForm()
    return render(request, 'maintenance/request_form.html', {
        'form': form, 'page_title': 'Gửi phản ánh'
    })


@login_required
def request_detail(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)

    # Kiểm tra quyền xem
    if request.user.role == 'citizen' and req.reported_by != request.user and not req.is_anonymous:
        messages.error(request, 'Bạn không có quyền xem phản ánh này.')
        return redirect('maintenance:request_list')

    comment_form = MaintenanceCommentForm()
    comments = req.comments.filter(is_internal=False) if request.user.role == 'citizen' else req.comments.all()
    photos = req.photos.all()

    return render(request, 'maintenance/request_detail.html', {
        'req': req, 'comment_form': comment_form,
        'comments': comments, 'photos': photos,
        'page_title': req.title,
    })


@login_required
def request_cancel(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk, reported_by=request.user)
    if req.status in ('pending', 'received'):
        req.status = 'cancelled'
        req.save()
        messages.success(request, 'Đã hủy phản ánh.')
    else:
        messages.error(request, 'Không thể hủy phản ánh ở trạng thái này.')
    return redirect('maintenance:request_detail', pk=pk)


@login_required
def request_rate(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk, reported_by=request.user)
    if request.method == 'POST' and req.status == 'completed':
        rating = int(request.POST.get('rating', 3))
        feedback = request.POST.get('feedback', '')
        req.citizen_rating = max(1, min(5, rating))
        req.citizen_feedback = feedback
        req.save()
        messages.success(request, 'Cảm ơn bạn đã đánh giá!')
    return redirect('maintenance:request_detail', pk=pk)


@login_required
@staff_required
def request_receive(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if req.status == 'pending':
        req.status = 'received'
        req.save()
        _send_notification(req, 'Phản ánh của bạn đã được tiếp nhận.')
        messages.success(request, 'Đã tiếp nhận phản ánh.')
    return redirect('maintenance:request_detail', pk=pk)


@login_required
@staff_required
def request_assign(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        from accounts.models import User
        staff = get_object_or_404(User, pk=user_id)
        req.assigned_to = staff
        req.assigned_at = timezone.now()
        req.status = 'assigned'
        req.save()
        _send_notification(req, f'Phản ánh đã được phân công cho {staff.get_full_name()}.')
        messages.success(request, f'Đã phân công cho {staff.get_full_name()}.')
        return JsonResponse({'success': True})
    from accounts.models import User
    staff_list = User.objects.filter(role__in=['staff', 'manager']).order_by('first_name')
    return render(request, 'maintenance/assign.html', {'req': req, 'staff_list': staff_list})


@login_required
@staff_required
def request_update_progress(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        actual_cost = request.POST.get('actual_cost', 0)

        if new_status in dict(MaintenanceRequest.STATUS_CHOICES):
            req.status = new_status
            req.processing_note = note
            if actual_cost:
                req.actual_cost = actual_cost

            if new_status == 'in_progress' and not req.started_at:
                req.started_at = timezone.now()
            elif new_status == 'completed':
                req.completed_at = timezone.now()

            req.save()

            # Upload ảnh sau sửa chữa
            for f in request.FILES.getlist('after_photos'):
                MaintenancePhoto.objects.create(
                    request=req, image=f, phase='after', uploaded_by=request.user
                )

            _send_notification(req, f'Trạng thái phản ánh cập nhật: {req.get_status_display()}')
            messages.success(request, 'Đã cập nhật tiến độ.')

    return redirect('maintenance:request_detail', pk=pk)


@login_required
def add_comment(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        form = MaintenanceCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.request = req
            comment.author = request.user
            if request.user.role == 'citizen':
                comment.is_internal = False
            else:
                comment.is_internal = request.POST.get('is_internal') == 'on'
            comment.save()
            messages.success(request, 'Đã thêm bình luận.')
    return redirect('maintenance:request_detail', pk=pk)


@login_required
def schedule_list(request):
    schedules = MaintenanceSchedule.objects.prefetch_related('assigned_to').all()
    paginator = Paginator(schedules, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'maintenance/schedule_list.html', {
        'page_obj': page, 'page_title': 'Lịch bảo trì'
    })


@login_required
@staff_required
def schedule_create(request):
    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            schedule.save()
            form.save_m2m()
            messages.success(request, 'Đã tạo lịch bảo trì.')
            return redirect('maintenance:schedule_list')
    else:
        form = MaintenanceScheduleForm()
    return render(request, 'maintenance/schedule_form.html', {'form': form, 'page_title': 'Tạo lịch bảo trì'})


@login_required
def maintenance_stats(request):
    from django.db.models import Count, Avg, Sum
    stats = {
        'by_status': list(MaintenanceRequest.objects.values('status').annotate(count=Count('id'))),
        'by_type': list(MaintenanceRequest.objects.values('incident_type').annotate(count=Count('id'))),
        'by_priority': list(MaintenanceRequest.objects.values('priority').annotate(count=Count('id'))),
        'avg_rating': MaintenanceRequest.objects.filter(citizen_rating__isnull=False).aggregate(avg=Avg('citizen_rating'))['avg'],
        'total_cost': MaintenanceRequest.objects.aggregate(total=Count('actual_cost'))['total'],
    }
    return render(request, 'maintenance/stats.html', {'stats': stats, 'page_title': 'Thống kê bảo trì'})


def _send_notification(req, message):
    try:
        from notifications.models import Notification
        if req.reported_by:
            Notification.objects.create(
                recipient=req.reported_by,
                title='Cập nhật phản ánh',
                message=message,
                notification_type='maintenance',
                related_object_id=req.pk,
            )
    except Exception:
        pass
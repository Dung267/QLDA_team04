from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notif_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    if notif_type:
        notifications = notifications.filter(notification_type=notif_type)
    if date_from:
        notifications = notifications.filter(created_at__date__gte=date_from)
    paginator = Paginator(notifications, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'notifications/list.html', {
        'page_obj': page,
        'type_choices': Notification.TYPE_CHOICES,
        'page_title': 'Thông báo',
    })


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return JsonResponse({'success': True})


@login_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    return redirect('notifications:list')


@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})
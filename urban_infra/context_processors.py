from django.conf import settings


def global_context(request):
    context = {
        'SYSTEM_NAME': settings.SYSTEM_NAME,
        'SYSTEM_SHORT_NAME': settings.SYSTEM_SHORT_NAME,
        'SYSTEM_VERSION': settings.SYSTEM_VERSION,
    }
    if request.user.is_authenticated:
        from notifications.models import Notification
        context['unread_count'] = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    return context
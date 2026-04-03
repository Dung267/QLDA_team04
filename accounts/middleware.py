from django.utils import timezone
from django.conf import settings


class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            from .models import UserSession
            UserSession.objects.filter(
                session_key=request.session.session_key
            ).update(last_activity=timezone.now())

        response = self.get_response(request)
        return response
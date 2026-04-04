from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import APIIntegration, WebhookLog
from .serializers import APIIntegrationSerializer, WebhookLogSerializer


class IntegrationListAPIView(generics.ListCreateAPIView):
    queryset = APIIntegration.objects.all()
    serializer_class = APIIntegrationSerializer
    permission_classes = [permissions.IsAdminUser]


class IntegrationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = APIIntegration.objects.all()
    serializer_class = APIIntegrationSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def test_integration_api(request, pk):
    from django.utils import timezone
    try:
        integration = APIIntegration.objects.get(pk=pk)
        import requests as req
        try:
            resp = req.get(integration.endpoint, timeout=5)
            integration.status = 'active' if resp.status_code < 400 else 'error'
            integration.error_message = '' if resp.status_code < 400 else f'HTTP {resp.status_code}'
        except Exception as e:
            integration.status = 'error'
            integration.error_message = str(e)
        integration.last_sync = timezone.now()
        integration.save()
        return Response({'status': integration.status, 'error': integration.error_message})
    except APIIntegration.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


class WebhookLogListAPIView(generics.ListAPIView):
    queryset = WebhookLog.objects.order_by('-created_at')[:100]
    serializer_class = WebhookLogSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webhook_receive_api(request):
    """Endpoint to receive incoming webhooks"""
    WebhookLog.objects.create(
        event_type=request.data.get('event', 'unknown'),
        payload=str(request.data),
        response_code=200,
        is_success=True,
    )
    return Response({'received': True})

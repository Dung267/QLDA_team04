from rest_framework import serializers
from .models import APIIntegration, WebhookLog


class APIIntegrationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = APIIntegration
        fields = '__all__'
        extra_kwargs = {
            'api_key': {'write_only': True}  # Never expose API keys in responses
        }


class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = '__all__'

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class APIIntegration(models.Model):
    STATUS_CHOICES = [('active','Hoạt động'),('inactive','Không hoạt động'),('error','Lỗi')]
    name = models.CharField('Tên tích hợp', max_length=100)
    api_key = models.CharField('API Key', max_length=300, blank=True)
    endpoint = models.URLField('Endpoint URL', blank=True)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='inactive')
    last_sync = models.DateTimeField('Đồng bộ lần cuối', null=True, blank=True)
    error_message = models.TextField('Lỗi', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Tích hợp API'
    def __str__(self): return self.name

class WebhookLog(models.Model):
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, related_name='webhook_logs', null=True, blank=True)
    event_type = models.CharField(max_length=100)
    payload = models.TextField()
    response_code = models.IntegerField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

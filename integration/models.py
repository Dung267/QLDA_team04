from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class APIIntegration(models.Model):
    STATUS_CHOICES = [('active','Hoạt động'),('inactive','Tắt'),('error','Lỗi')]
    name = models.CharField('Tên tích hợp', max_length=100)
    base_url = models.URLField('URL cơ sở')
    api_key = models.CharField('API Key', max_length=200, blank=True)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='inactive')
    last_sync = models.DateTimeField('Đồng bộ lần cuối', null=True, blank=True)
    sync_interval_minutes = models.IntegerField('Tần suất đồng bộ (phút)', default=60)
    is_webhook = models.BooleanField('Là Webhook', default=False)
    description = models.TextField('Mô tả', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tích hợp API'
        verbose_name_plural = 'Tích hợp API'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class APILog(models.Model):
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE, related_name='logs')
    method = models.CharField('Phương thức', max_length=10)
    endpoint = models.CharField('Endpoint', max_length=500)
    request_data = models.JSONField('Dữ liệu gửi', default=dict, blank=True)
    response_status = models.IntegerField('HTTP Status', null=True, blank=True)
    response_data = models.JSONField('Dữ liệu nhận', default=dict, blank=True)
    is_success = models.BooleanField('Thành công', default=True)
    error_message = models.TextField('Lỗi', blank=True)
    duration_ms = models.FloatField('Thời gian (ms)', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log API'
        ordering = ['-created_at']

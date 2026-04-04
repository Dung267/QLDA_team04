from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    TYPE_CHOICES = [
        ('maintenance', 'Bảo trì'),
        ('flood', 'Ngập lụt'),
        ('system', 'Hệ thống'),
        ('emergency', 'Khẩn cấp'),
        ('general', 'Thông thường'),
        ('reminder', 'Nhắc nhở'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                                   verbose_name='Người nhận')
    title = models.CharField('Tiêu đề', max_length=200)
    message = models.TextField('Nội dung')
    notification_type = models.CharField('Loại', max_length=15, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField('Đã đọc', default=False)
    related_object_id = models.IntegerField('ID đối tượng liên quan', null=True, blank=True)
    action_url = models.CharField('URL hành động', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField('Đọc lúc', null=True, blank=True)

    class Meta:
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    def mark_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationHistory(models.Model):
    """Lịch sử tất cả thông báo đã gửi"""
    CHANNEL_CHOICES = [('email', 'Email'), ('sms', 'SMS'), ('push', 'Push'), ('system', 'Hệ thống')]

    title = models.CharField('Tiêu đề', max_length=200)
    message = models.TextField('Nội dung')
    channel = models.CharField('Kênh', max_length=10, choices=CHANNEL_CHOICES)
    recipient_count = models.IntegerField('Số người nhận', default=0)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử thông báo'
        ordering = ['-created_at']

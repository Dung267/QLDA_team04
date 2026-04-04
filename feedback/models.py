from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class SystemFeedback(models.Model):
    STATUS_CHOICES = [('new','Mới'),('reviewed','Đã xem xét'),('resolved','Đã xử lý'),('hidden','Đã ẩn')]
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_anonymous = models.BooleanField('Ẩn danh', default=False)
    rating = models.IntegerField('Đánh giá (1-5)')
    content = models.TextField('Nội dung')
    category = models.CharField('Phân loại', max_length=100, blank=True)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='new')
    admin_reply = models.TextField('Phản hồi quản trị', blank=True)
    is_important = models.BooleanField('Quan trọng', default=False)
    is_spam = models.BooleanField('Spam', default=False)
    likes = models.IntegerField('Lượt thích', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Phản hồi hệ thống'
        verbose_name_plural = 'Phản hồi hệ thống'
        ordering = ['-created_at']
    def __str__(self): return f"Phản hồi #{self.pk} - {self.rating}★"

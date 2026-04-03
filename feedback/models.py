from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class SystemFeedback(models.Model):
    STATUS_CHOICES = [('new','Mới'),('reviewed','Đã xem'),('resolved','Đã xử lý'),('hidden','Ẩn')]
    CATEGORY_CHOICES = [
        ('bug','Lỗi'),('suggestion','Góp ý'),('complaint','Khiếu nại'),
        ('compliment','Khen ngợi'),('other','Khác'),
    ]

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_feedbacks')
    is_anonymous = models.BooleanField('Ẩn danh', default=False)
    category = models.CharField('Danh mục', max_length=15, choices=CATEGORY_CHOICES, default='suggestion')
    title = models.CharField('Tiêu đề', max_length=200)
    content = models.TextField('Nội dung')
    rating = models.IntegerField('Đánh giá (1-5)', null=True, blank=True)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='new')
    admin_reply = models.TextField('Phản hồi quản trị viên', blank=True)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='replied_feedbacks')
    replied_at = models.DateTimeField(null=True, blank=True)
    is_important = models.BooleanField('Quan trọng', default=False)
    is_reported = models.BooleanField('Bị báo cáo', default=False)
    like_count = models.IntegerField('Lượt thích', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phản hồi hệ thống'
        verbose_name_plural = 'Phản hồi hệ thống'
        ordering = ['-created_at']

    def __str__(self):
        author_name = self.author.username if self.author and not self.is_anonymous else 'Ẩn danh'
        return f"{author_name}: {self.title[:60]}"

    def average_rating(self):
        from django.db.models import Avg
        return SystemFeedback.objects.aggregate(avg=Avg('rating'))['avg']

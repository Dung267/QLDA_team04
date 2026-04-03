from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField('Đánh giá', null=True, blank=True)
    feedback = models.TextField('Phản hồi', blank=True)

    class Meta:
        verbose_name = 'Phiên chat'
        ordering = ['-started_at']

    def __str__(self):
        return f"Chat {self.session_id[:8]}..."


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'Người dùng'), ('bot', 'Bot')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField('Vai trò', max_length=5, choices=ROLE_CHOICES)
    content = models.TextField('Nội dung')
    topic = models.CharField('Chủ đề', max_length=100, blank=True)
    was_understood = models.BooleanField('Được hiểu', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tin nhắn chat'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"


class FAQItem(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Chung'), ('maintenance', 'Bảo trì'),
        ('flood', 'Ngập lụt'), ('inspection', 'Đăng kiểm'),
        ('permit', 'Giấy phép'),
    ]
    question = models.TextField('Câu hỏi')
    answer = models.TextField('Câu trả lời')
    category = models.CharField('Danh mục', max_length=20, choices=CATEGORY_CHOICES, default='general')
    keywords = models.TextField('Từ khóa', blank=True, help_text='Phân cách bằng dấu phẩy')
    view_count = models.IntegerField('Lượt xem', default=0)
    is_active = models.BooleanField('Hiện', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['-view_count']

    def __str__(self):
        return self.question[:80]

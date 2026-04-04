from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Phiên chat'
        verbose_name_plural = 'Phiên chat'
        ordering = ['-started_at']

    def __str__(self): return f"Chat {self.session_id[:8]}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [('user','Người dùng'),('bot','Bot')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=5, choices=SENDER_CHOICES)
    content = models.TextField()
    is_understood = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class FAQ(models.Model):
    question = models.CharField('Câu hỏi', max_length=300)
    answer = models.TextField('Câu trả lời')
    category = models.CharField('Lĩnh vực', max_length=100, blank=True)
    keywords = models.TextField('Từ khóa (cách nhau dấu phẩy)', blank=True)
    view_count = models.IntegerField('Số lần xem', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['-view_count']

    def __str__(self): return self.question

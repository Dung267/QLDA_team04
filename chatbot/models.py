from django.conf import settings
from django.db import models

from common.models import TimeStampedModel

# Create your models here.
class ChatSession(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    channel = models.CharField(max_length=20, default="WEB")

class ChatMessage(TimeStampedModel):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10)  # USER, BOT
    content = models.TextField()
    intent = models.CharField(max_length=50, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
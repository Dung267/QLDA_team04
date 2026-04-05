from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ReportTemplate(models.Model):
    TYPE_CHOICES = [('monthly','Tháng'),('quarterly','Quý'),('yearly','Năm'),('custom','Tùy chỉnh')]
    name = models.CharField('Tên mẫu báo cáo', max_length=200)
    report_type = models.CharField('Loại', max_length=15, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Mẫu báo cáo'
    def __str__(self): return self.name

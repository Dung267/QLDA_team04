from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Report(models.Model):
    TYPE_CHOICES = [('monthly','Tháng'),('quarterly','Quý'),('yearly','Năm'),('custom','Tùy chỉnh')]
    CATEGORY_CHOICES = [
        ('maintenance','Bảo trì'),('infrastructure','Hạ tầng'),
        ('inventory','Vật tư'),('hr','Nhân sự'),('financial','Tài chính'),
    ]
    FORMAT_CHOICES = [('pdf','PDF'),('excel','Excel'),('word','Word')]

    title = models.CharField('Tiêu đề báo cáo', max_length=300)
    report_type = models.CharField('Loại', max_length=10, choices=TYPE_CHOICES)
    category = models.CharField('Danh mục', max_length=15, choices=CATEGORY_CHOICES)
    period_start = models.DateField('Từ ngày')
    period_end = models.DateField('Đến ngày')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField('File', upload_to='reports/', null=True, blank=True)
    file_format = models.CharField('Định dạng', max_length=5, choices=FORMAT_CHOICES, default='pdf')
    data_snapshot = models.JSONField('Dữ liệu snapshot', default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Báo cáo'
        verbose_name_plural = 'Báo cáo'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

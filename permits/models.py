from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ConstructionPermit(models.Model):
    STATUS_CHOICES = [
        ('draft','Nháp'),('submitted','Đã nộp'),('received','Đã tiếp nhận'),
        ('reviewing','Đang xét duyệt'),('additional_required','Cần bổ sung'),
        ('approved','Đã phê duyệt'),('rejected','Từ chối'),
        ('construction','Đang thi công'),('completed','Hoàn thành'),
        ('suspended','Tạm dừng'),
    ]
    permit_number = models.CharField('Số giấy phép', max_length=50, blank=True)
    title = models.CharField('Tiêu đề', max_length=300)
    description = models.TextField('Mô tả công trình')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permit_applications')
    contractor_name = models.CharField('Tên nhà thầu', max_length=200, blank=True)
    location = models.CharField('Địa điểm thi công', max_length=300)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    start_date = models.DateField('Ngày bắt đầu', null=True, blank=True)
    end_date = models.DateField('Ngày kết thúc', null=True, blank=True)
    status = models.CharField('Trạng thái', max_length=25, choices=STATUS_CHOICES, default='draft')
    rejection_reason = models.TextField('Lý do từ chối', blank=True)
    additional_required = models.TextField('Yêu cầu bổ sung', blank=True)
    violation_warning = models.TextField('Cảnh báo vi phạm', blank=True)
    assigned_reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewing_permits')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_permits')
    impact_assessment = models.TextField('Đánh giá tác động hạ tầng', blank=True)
    progress_report = models.TextField('Báo cáo tiến độ', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = 'Giấy phép thi công'
        verbose_name_plural = 'Giấy phép thi công'
        ordering = ['-created_at']
    def __str__(self): return f"{self.permit_number or 'Nháp'} - {self.title}"

class PermitDocument(models.Model):
    permit = models.ForeignKey(ConstructionPermit, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField('Tên tài liệu', max_length=200)
    file = models.FileField('Tệp', upload_to='permits/documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Tài liệu hồ sơ'

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class ConstructionPermit(models.Model):
    STATUS_CHOICES = [
        ('draft','Nháp'),('submitted','Đã nộp'),('received','Đã tiếp nhận'),
        ('legal_check','Kiểm tra pháp lý'),('additional_needed','Cần bổ sung'),
        ('approved','Đã duyệt'),('rejected','Từ chối'),('issued','Đã cấp phép'),
        ('suspended','Tạm dừng'),('completed','Hoàn thành'),
    ]
    PERMIT_TYPES = [
        ('road_work','Thi công đường'),('underground','Hạ ngầm'),
        ('bridge','Cầu cống'),('building','Xây dựng'),('other','Khác'),
    ]

    permit_number = models.CharField('Số hồ sơ', max_length=50, blank=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permit_applications')
    permit_type = models.CharField('Loại giấy phép', max_length=15, choices=PERMIT_TYPES)
    project_name = models.CharField('Tên công trình', max_length=300)
    description = models.TextField('Mô tả')
    address = models.TextField('Địa chỉ thi công')
    start_date = models.DateField('Ngày bắt đầu dự kiến', null=True, blank=True)
    end_date = models.DateField('Ngày kết thúc dự kiến', null=True, blank=True)
    status = models.CharField('Trạng thái', max_length=20, choices=STATUS_CHOICES, default='draft')
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='assigned_permits', verbose_name='Cán bộ xử lý')
    rejection_reason = models.TextField('Lý do từ chối', blank=True)
    additional_required = models.TextField('Tài liệu cần bổ sung', blank=True)
    infrastructure_impact = models.TextField('Tác động hạ tầng', blank=True)
    issued_at = models.DateTimeField('Ngày cấp phép', null=True, blank=True)
    permit_expires_at = models.DateField('Hạn giấy phép', null=True, blank=True)
    is_extended = models.BooleanField('Đã gia hạn', default=False)
    revoked_at = models.DateTimeField('Ngày thu hồi', null=True, blank=True)
    revocation_reason = models.TextField('Lý do thu hồi', blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Giấy phép thi công'
        verbose_name_plural = 'Giấy phép thi công'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.permit_number or 'Nháp'} - {self.project_name}"

    def save(self, *args, **kwargs):
        if not self.permit_number and self.status == 'submitted':
            from django.utils import timezone
            self.permit_number = f"GP{timezone.now().strftime('%Y%m')}{str(self.pk or 0).zfill(4)}"
        super().save(*args, **kwargs)


class PermitDocument(models.Model):
    permit = models.ForeignKey(ConstructionPermit, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField('File', upload_to='permits/docs/')
    doc_type = models.CharField('Loại tài liệu', max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tài liệu hồ sơ'

    def __str__(self):
        return f"{self.doc_type} - {self.permit}"


class PermitInspection(models.Model):
    permit = models.ForeignKey(ConstructionPermit, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    inspection_date = models.DateField('Ngày kiểm tra')
    notes = models.TextField('Ghi chú')
    has_violation = models.BooleanField('Có vi phạm', default=False)
    violation_details = models.TextField('Chi tiết vi phạm', blank=True)
    photos = models.ImageField('Ảnh', upload_to='permits/inspections/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kiểm tra hiện trường'
        ordering = ['-inspection_date']

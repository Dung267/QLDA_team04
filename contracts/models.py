from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Contractor(models.Model):
    name = models.CharField('Tên nhà thầu', max_length=200)
    tax_code = models.CharField('Mã số thuế', max_length=20, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Nhà thầu'
        verbose_name_plural = 'Nhà thầu'

    def __str__(self):
        return self.name


class Tender(models.Model):
    STATUS_CHOICES = [('open','Đang mở'),('closed','Đã đóng'),('awarded','Đã trao thầu'),('cancelled','Hủy')]
    title = models.CharField('Tiêu đề', max_length=300)
    description = models.TextField('Mô tả')
    budget = models.DecimalField('Ngân sách (VNĐ)', max_digits=18, decimal_places=0)
    deadline = models.DateField('Hạn nộp hồ sơ')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='open')
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Đấu thầu'
        verbose_name_plural = 'Đấu thầu'

    def __str__(self):
        return self.title


class Contract(models.Model):
    STATUS_CHOICES = [('draft','Nháp'),('active','Đang hiệu lực'),('completed','Hoàn thành'),('terminated','Chấm dứt')]
    contract_number = models.CharField('Số hợp đồng', max_length=50, unique=True)
    title = models.CharField('Tên hợp đồng', max_length=300)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='contracts')
    tender = models.ForeignKey(Tender, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField('Giá trị (VNĐ)', max_digits=18, decimal_places=0)
    start_date = models.DateField('Ngày bắt đầu')
    end_date = models.DateField('Ngày kết thúc')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='draft')
    description = models.TextField('Nội dung', blank=True)
    terms = models.TextField('Điều khoản', blank=True)
    guaranty_amount = models.DecimalField('Bảo lãnh (VNĐ)', max_digits=18, decimal_places=0, default=0)
    paid_amount = models.DecimalField('Đã thanh toán', max_digits=18, decimal_places=0, default=0)
    progress_percent = models.IntegerField('Tiến độ %', default=0)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_contracts')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hợp đồng'
        verbose_name_plural = 'Hợp đồng'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    @property
    def remaining_days(self):
        from django.utils import timezone
        return (self.end_date - timezone.now().date()).days

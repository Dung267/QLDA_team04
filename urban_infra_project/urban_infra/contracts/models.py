from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Contractor(models.Model):
    name = models.CharField('Tên nhà thầu', max_length=200)
    tax_code = models.CharField('Mã số thuế', max_length=20, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    representative = models.CharField('Người đại diện', max_length=100, blank=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Nhà thầu'
        verbose_name_plural = 'Nhà thầu'
    def __str__(self): return self.name

class Contract(models.Model):
    STATUS_CHOICES = [('draft','Nháp'),('active','Đang hiệu lực'),('completed','Hoàn thành'),('terminated','Chấm dứt'),('expired','Hết hạn')]
    contract_number = models.CharField('Số hợp đồng', max_length=50, unique=True)
    title = models.CharField('Tiêu đề', max_length=300)
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, related_name='contracts')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='draft')
    value = models.DecimalField('Giá trị (VNĐ)', max_digits=18, decimal_places=0, default=0)
    start_date = models.DateField('Ngày bắt đầu')
    end_date = models.DateField('Ngày kết thúc')
    terms = models.TextField('Điều khoản', blank=True)
    description = models.TextField('Mô tả', blank=True)
    guaranty = models.DecimalField('Bảo lãnh', max_digits=18, decimal_places=0, default=0)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_contracts')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    document = models.FileField('Tài liệu hợp đồng', upload_to='contracts/', null=True, blank=True)
    progress_percent = models.IntegerField('Tiến độ (%)', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Hợp đồng'
        verbose_name_plural = 'Hợp đồng'
        ordering = ['-created_at']
    def __str__(self): return f"{self.contract_number} - {self.title}"

class Tender(models.Model):
    STATUS_CHOICES = [('open','Đang mở'),('closed','Đã đóng'),('awarded','Đã trao thầu'),('cancelled','Hủy')]
    title = models.CharField('Tiêu đề gói thầu', max_length=300)
    description = models.TextField('Mô tả')
    budget = models.DecimalField('Ngân sách (VNĐ)', max_digits=18, decimal_places=0, default=0)
    deadline = models.DateTimeField('Hạn nộp hồ sơ')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='open')
    awarded_to = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True, related_name='awarded_tenders')
    result_contract = models.OneToOneField(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='tender')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Gói thầu'
        verbose_name_plural = 'Gói thầu'
        ordering = ['-created_at']
    def __str__(self): return self.title

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Department(models.Model):
    name = models.CharField('Phòng ban', max_length=100)
    code = models.CharField('Mã', max_length=20, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Phòng ban'
        verbose_name_plural = 'Phòng ban'

    def __str__(self): return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField('Mã nhân viên', max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.CharField('Chức vụ', max_length=100, blank=True)
    hire_date = models.DateField('Ngày vào làm', null=True, blank=True)
    contract_type = models.CharField('Loại hợp đồng', max_length=50, blank=True)
    salary = models.DecimalField('Lương (VNĐ)', max_digits=15, decimal_places=0, default=0)
    phone_work = models.CharField('SĐT công việc', max_length=15, blank=True)
    emergency_contact = models.CharField('Liên hệ khẩn cấp', max_length=200, blank=True)
    is_active = models.BooleanField('Đang làm việc', default=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'

    def __str__(self): return f"{self.user.get_full_name()} ({self.employee_id})"


class WorkAssignment(models.Model):
    STATUS_CHOICES = [('todo','Chưa làm'),('in_progress','Đang làm'),('done','Hoàn thành'),('cancelled','Hủy')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    due_date = models.DateField('Hạn hoàn thành', null=True, blank=True)
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='todo')
    completion_note = models.TextField('Ghi chú hoàn thành', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phân công công việc'
        verbose_name_plural = 'Phân công công việc'
        ordering = ['due_date']

    def __str__(self): return f"{self.employee} - {self.title}"


class LeaveRequest(models.Model):
    TYPE_CHOICES = [('annual','Phép năm'),('sick','Nghỉ bệnh'),('unpaid','Không lương'),('other','Khác')]
    STATUS_CHOICES = [('pending','Chờ duyệt'),('approved','Đã duyệt'),('rejected','Từ chối')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField('Loại phép', max_length=10, choices=TYPE_CHOICES)
    start_date = models.DateField('Từ ngày')
    end_date = models.DateField('Đến ngày')
    reason = models.TextField('Lý do')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Đơn nghỉ phép'
        verbose_name_plural = 'Đơn nghỉ phép'

    def __str__(self): return f"{self.employee} - {self.start_date}"


class Training(models.Model):
    title = models.CharField('Khóa đào tạo', max_length=200)
    description = models.TextField(blank=True)
    trainer = models.CharField('Giảng viên', max_length=100, blank=True)
    start_date = models.DateField('Ngày bắt đầu')
    end_date = models.DateField('Ngày kết thúc')
    participants = models.ManyToManyField(Employee, blank=True, related_name='trainings')
    certificate_required = models.BooleanField('Cấp chứng chỉ', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Đào tạo'
        verbose_name_plural = 'Đào tạo'

    def __str__(self): return self.title

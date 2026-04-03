from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Department(models.Model):
    name = models.CharField('Tên phòng ban', max_length=100)
    code = models.CharField('Mã', max_length=20, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Phòng ban'
        verbose_name_plural = 'Phòng ban'

    def __str__(self):
        return self.name


class Employee(models.Model):
    EMPLOYMENT_STATUS = [('active','Đang làm việc'),('leave','Nghỉ phép'),('resigned','Đã nghỉ việc')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField('Mã nhân viên', max_length=20, unique=True)
    position = models.CharField('Chức vụ', max_length=100)
    employment_status = models.CharField('Trạng thái', max_length=10, choices=EMPLOYMENT_STATUS, default='active')
    hire_date = models.DateField('Ngày vào làm')
    contract_end_date = models.DateField('Hết hạn hợp đồng', null=True, blank=True)
    salary = models.DecimalField('Lương', max_digits=12, decimal_places=0, default=0)
    certifications = models.TextField('Chứng chỉ', blank=True)
    skills = models.TextField('Kỹ năng', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"


class WorkAssignment(models.Model):
    STATUS_CHOICES = [('pending','Chờ'),('in_progress','Đang làm'),('completed','Hoàn thành'),('cancelled','Hủy')]
    PRIORITY_CHOICES = [('low','Thấp'),('normal','Bình thường'),('high','Cao'),('urgent','Khẩn cấp')]

    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_assignments')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField('Ưu tiên', max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField('Hạn nộp', null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.IntegerField('Tiến độ %', default=0)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Công việc'
        verbose_name_plural = 'Công việc'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.assigned_to.get_full_name()}"


class LeaveRequest(models.Model):
    LEAVE_TYPES = [('annual','Phép năm'),('sick','Ốm'),('maternity','Thai sản'),('unpaid','Không lương')]
    STATUS_CHOICES = [('pending','Chờ duyệt'),('approved','Chấp thuận'),('rejected','Từ chối')]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField('Loại nghỉ', max_length=15, choices=LEAVE_TYPES)
    start_date = models.DateField('Từ ngày')
    end_date = models.DateField('Đến ngày')
    reason = models.TextField('Lý do')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    rejection_reason = models.TextField('Lý do từ chối', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Yêu cầu nghỉ phép'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_leave_type_display()}"

    @property
    def days_count(self):
        return (self.end_date - self.start_date).days + 1


class Meeting(models.Model):
    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Nội dung', blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    participants = models.ManyToManyField(User, related_name='meetings', blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_at = models.DateTimeField('Thời gian')
    duration_minutes = models.IntegerField('Thời lượng (phút)', default=60)
    location = models.CharField('Địa điểm', max_length=200, blank=True)
    is_online = models.BooleanField('Trực tuyến', default=False)
    meeting_link = models.URLField('Link họp', blank=True)
    minutes = models.TextField('Biên bản', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cuộc họp'
        ordering = ['-scheduled_at']

    def __str__(self):
        return self.title

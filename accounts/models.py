from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên hệ thống'),
        ('manager', 'Quản lý'),
        ('staff', 'Cán bộ kỹ thuật'),
        ('inspector', 'Kiểm định viên'),
        ('citizen', 'Người dân'),
    ]

    role = models.CharField('Vai trò', max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField('Số điện thoại', max_length=15, blank=True)
    avatar = models.ImageField('Ảnh đại diện', upload_to='avatars/', blank=True, null=True)
    address = models.TextField('Địa chỉ', blank=True)
    district = models.CharField('Quận/Huyện', max_length=100, blank=True)
    ward = models.CharField('Phường/Xã', max_length=100, blank=True)
    is_locked = models.BooleanField('Bị khóa', default=False)
    locked_reason = models.TextField('Lý do khóa', blank=True)
    otp_secret = models.CharField(max_length=32, blank=True)
    two_factor_enabled = models.BooleanField('Xác thực 2 bước', default=False)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật', auto_now=True)

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_staff_member(self):
        return self.role in ('admin', 'manager', 'staff', 'inspector')


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField('Địa chỉ IP')
    user_agent = models.TextField('User Agent', blank=True)
    device_info = models.CharField('Thiết bị', max_length=255, blank=True)
    location = models.CharField('Vị trí', max_length=255, blank=True)
    is_successful = models.BooleanField('Đăng nhập thành công', default=True)
    is_suspicious = models.BooleanField('Đáng ngờ', default=False)
    created_at = models.DateTimeField('Thời gian', auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử đăng nhập'
        verbose_name_plural = 'Lịch sử đăng nhập'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class OTPVerification(models.Model):
    PURPOSE_CHOICES = [
        ('login', 'Đăng nhập'),
        ('reset_password', 'Đặt lại mật khẩu'),
        ('change_phone', 'Đổi số điện thoại'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    code = models.CharField('Mã OTP', max_length=6)
    purpose = models.CharField('Mục đích', max_length=20, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField('Đã sử dụng', default=False)
    expires_at = models.DateTimeField('Hết hạn')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTP'

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField('Session key', max_length=40, unique=True)
    ip_address = models.GenericIPAddressField('Địa chỉ IP')
    device_info = models.CharField('Thiết bị', max_length=255, blank=True)
    last_activity = models.DateTimeField('Hoạt động cuối', auto_now=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phiên đăng nhập'
        verbose_name_plural = 'Phiên đăng nhập'
        ordering = ['-last_activity']
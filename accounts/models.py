# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    OFFICER = "OFFICER", "Cán bộ"
    CITIZEN = "CITIZEN", "Người dân"
    TECHNICIAN = "TECHNICIAN", "Nhân viên bảo trì"


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CITIZEN
    )
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30)  # LOGIN, RESET_PASSWORD...
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

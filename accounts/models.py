from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    OFFICER = "OFFICER", "Cán bộ"
    CITIZEN = "CITIZEN", "Người dân"
    TECHNICIAN = "TECHNICIAN", "Nhân viên bảo trì"

class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CITIZEN)
    is_phone_verified = models.BooleanField(default=False)
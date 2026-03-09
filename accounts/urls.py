# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # Đăng ký tài khoản
    path('login/', views.login, name='login'),  # Đăng nhập tài khoản
    path('update/', views.update_account, name='update_account'),  # Cập nhật tài khoản
    path('password-change/', views.change_password, name='change_password'),  # Thay đổi mật khẩu
    path('profile/', views.profile, name='profile'),  # Xem hồ sơ người dùng
]
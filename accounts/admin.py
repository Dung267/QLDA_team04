from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginHistory, OTPVerification, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'phone', 'is_locked', 'is_active', 'date_joined']
    list_filter = ['role', 'is_locked', 'is_active', 'two_factor_enabled']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('role', 'phone', 'avatar', 'address', 'district', 'ward',
                       'is_locked', 'locked_reason', 'two_factor_enabled')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('role', 'phone', 'email', 'first_name', 'last_name')
        }),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_successful', 'is_suspicious', 'created_at']
    list_filter = ['is_successful', 'is_suspicious']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'created_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_info', 'last_activity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username', 'ip_address']
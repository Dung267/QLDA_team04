from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.role == 'admin' or request.user.is_superuser):
            messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
            return redirect('dashboard')
        return func(request, *args, **kwargs)
    return wrapper


def staff_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_staff_member:
            messages.error(request, 'Chức năng này chỉ dành cho cán bộ.')
            return redirect('dashboard')
        return func(request, *args, **kwargs)
    return wrapper


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, 'Bạn không có quyền truy cập.')
                return redirect('dashboard')
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
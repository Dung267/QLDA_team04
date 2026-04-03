from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from datetime import timedelta
import secrets
import string

from .models import User, LoginHistory, OTPVerification, UserSession
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    ChangePasswordForm, ForgotPasswordForm, OTPForm
)
from .decorators import admin_required, staff_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_locked:
                    messages.error(request, 'Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.')
                elif user.two_factor_enabled:
                    request.session['pending_user_id'] = user.id
                    return redirect('accounts:otp_verify')
                else:
                    login(request, user)
                    _log_login(request, user, True)
                    messages.success(request, f'Chào mừng {user.get_full_name() or user.username}!')
                    return redirect(request.GET.get('next', 'dashboard'))
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
                _log_failed_login(request, username)
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        UserSession.objects.filter(
            user=request.user,
            session_key=request.session.session_key
        ).update(is_active=False)
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('accounts:login')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'citizen'
            user.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công! Chào mừng bạn.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def otp_verify_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = OTPVerification.objects.filter(
                user=user, code=form.cleaned_data['code'],
                purpose='login', is_used=False
            ).first()

            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()
                login(request, user)
                del request.session['pending_user_id']
                _log_login(request, user, True)
                return redirect('dashboard')
            else:
                messages.error(request, 'Mã OTP không hợp lệ hoặc đã hết hạn.')
    else:
        # Tạo OTP mới
        _send_otp(user, 'login')
        form = OTPForm()

    return render(request, 'accounts/otp_verify.html', {'form': form})


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                _send_otp(user, 'reset_password')
                request.session['reset_user_id'] = user.id
                return redirect('accounts:reset_password')
            messages.error(request, 'Email không tồn tại trong hệ thống.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            # Đăng xuất tất cả thiết bị khác
            UserSession.objects.filter(user=user).exclude(
                session_key=request.session.session_key
            ).update(is_active=False)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def login_history_view(request):
    history = LoginHistory.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(history, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'accounts/login_history.html', {'page_obj': page})


# Admin views
@login_required
@admin_required
def user_list_view(request):
    users = User.objects.all().order_by('-date_joined')

    # Filters
    role = request.GET.get('role')
    district = request.GET.get('district')
    search = request.GET.get('search')

    if role:
        users = users.filter(role=role)
    if district:
        users = users.filter(district=district)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    paginator = Paginator(users, 25)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'accounts/user_list.html', {
        'page_obj': page,
        'roles': User.ROLE_CHOICES,
        'page_title': 'Danh sách người dùng',
    })


@login_required
@admin_required
def create_staff_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = request.POST.get('role', 'staff')
            # Tạo mật khẩu mạnh tự động
            password = _generate_strong_password()
            user.set_password(password)
            user.save()
            messages.success(request, f'Tạo tài khoản thành công! Mật khẩu: {password}')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/create_staff.html', {
        'form': form,
        'roles': [r for r in User.ROLE_CHOICES if r[0] != 'citizen'],
        'page_title': 'Tạo tài khoản cán bộ',
    })


@login_required
@admin_required
def lock_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_locked = True
        user.locked_reason = request.POST.get('reason', '')
        user.save()
        # Vô hiệu hóa tất cả session
        UserSession.objects.filter(user=user).update(is_active=False)
        messages.success(request, f'Đã khóa tài khoản {user.username}.')
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@admin_required
def unlock_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_locked = False
    user.locked_reason = ''
    user.save()
    messages.success(request, f'Đã mở khóa tài khoản {user.username}.')
    return redirect('accounts:user_list')


@login_required
@admin_required
def delete_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Đã xóa tài khoản.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/confirm_delete.html', {'user_obj': user})


@login_required
@admin_required
def assign_role_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(User.ROLE_CHOICES):
            user.role = new_role
            user.save()
            return JsonResponse({'success': True, 'role': user.get_role_display()})
    return JsonResponse({'error': 'Invalid role'}, status=400)


@login_required
def active_sessions_view(request):
    sessions = UserSession.objects.filter(user=request.user, is_active=True)
    return render(request, 'accounts/sessions.html', {'sessions': sessions})


@login_required
def revoke_session_view(request, pk):
    session = get_object_or_404(UserSession, pk=pk, user=request.user)
    session.is_active = False
    session.save()
    messages.success(request, 'Đã thu hồi phiên đăng nhập.')
    return redirect('accounts:sessions')


@login_required
def logout_all_devices_view(request):
    UserSession.objects.filter(user=request.user).update(is_active=False)
    logout(request)
    messages.info(request, 'Đã đăng xuất khỏi tất cả thiết bị.')
    return redirect('accounts:login')


# Helpers
def _generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + '!@#$%'
    return ''.join(secrets.choice(chars) for _ in range(length))


def _send_otp(user, purpose):
    import random
    code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=5)
    OTPVerification.objects.create(
        user=user, code=code, purpose=purpose, expires_at=expires_at
    )
    # TODO: gửi qua email/SMS thực tế
    print(f"OTP for {user.username}: {code}")


def _log_login(request, user, success):
    ip = request.META.get('REMOTE_ADDR', '')
    agent = request.META.get('HTTP_USER_AGENT', '')
    LoginHistory.objects.create(
        user=user, ip_address=ip or '127.0.0.1',
        user_agent=agent, is_successful=success
    )
    if request.session.session_key:
        UserSession.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={
                'user': user,
                'ip_address': ip or '127.0.0.1',
                'device_info': agent[:255],
            }
        )


def _log_failed_login(request, username):
    user = User.objects.filter(username=username).first()
    if user:
        ip = request.META.get('REMOTE_ADDR', '')
        LoginHistory.objects.create(
            user=user, ip_address=ip or '127.0.0.1',
            is_successful=False
        )
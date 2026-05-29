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
    ChangePasswordForm, ForgotPasswordForm, OTPForm, StaffCreateForm
)
from .decorators import admin_required, staff_required


DA_NANG_DISTRICTS = [
    'Hải Châu',
    'Thanh Khê',
    'Liên Chiểu',
    'Sơn Trà',
    'Ngũ Hành Sơn',
    'Cẩm Lệ',
    'Hòa Vang',
]


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
    """
    Đổi mật khẩu cho người dùng đang đăng nhập.

    - Dùng form đổi mật khẩu chuẩn của Django (đã bọc lại trong `ChangePasswordForm`).
    - Sau khi đổi mật khẩu: giữ phiên hiện tại (update_session_auth_hash) và thu hồi các phiên khác.
    - Luôn bắt lỗi để tránh làm gián đoạn luồng đăng nhập của người dùng.
    """
    try:
        if request.method == 'POST':
            form = ChangePasswordForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                # Thu hồi các phiên khác để tăng an toàn
                UserSession.objects.filter(user=user).exclude(
                    session_key=request.session.session_key
                ).update(is_active=False)
                messages.success(request, 'Đổi mật khẩu thành công!')
                return redirect('accounts:profile')
        else:
            form = ChangePasswordForm(request.user)
        return render(request, 'accounts/change_password.html', {'form': form, 'page_title': 'Đổi mật khẩu'})
    except Exception as exc:
        messages.error(request, f'Không thể đổi mật khẩu: {exc}')
        return redirect('accounts:profile')


@login_required
def login_history_view(request):
    """
    Hiển thị lịch sử đăng nhập của người dùng.

    Thông tin hiển thị: thời gian, IP, thiết bị (từ user_agent/device_info), trạng thái thành công/thất bại.
    """
    try:
        history = LoginHistory.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(history, 20)
        page = paginator.get_page(request.GET.get('page', 1))
        return render(
            request,
            'accounts/login_history.html',
            {'page_obj': page, 'page_title': 'Lịch sử đăng nhập'},
        )
    except Exception as exc:
        messages.error(request, f'Không thể tải lịch sử đăng nhập: {exc}')
        return render(request, 'accounts/login_history.html', {'page_obj': None, 'page_title': 'Lịch sử đăng nhập'})


# Admin views
@login_required
@admin_required
def user_list_view(request):
    """
    Hiển thị danh sách người dùng kèm bộ lọc (vai trò, quận, tìm kiếm).

    - Vai trò: chuẩn hóa theo backlog UI (Admin/Cán bộ/Người dân).
    - Quận: ưu tiên danh sách mẫu theo bối cảnh Đà Nẵng; đồng thời vẫn lọc được theo dữ liệu thật trong DB.
    """
    try:
        users = User.objects.all().order_by('-date_joined')

        role = (request.GET.get('role') or '').strip()
        district = (request.GET.get('district') or '').strip()
        search = (request.GET.get('search') or '').strip()

        if role:
            # Đồng bộ theo 3 nhãn UI: Admin / Cán bộ / Người dân
            # - Admin: role=admin (và/hoặc superuser)
            # - Cán bộ: staff/manager/inspector
            # - Người dân: citizen
            if role == 'admin':
                users = users.filter(Q(role='admin') | Q(is_superuser=True))
            elif role == 'staff':
                users = users.filter(role__in=['staff', 'manager', 'inspector'])
            elif role == 'citizen':
                users = users.filter(role='citizen')
            else:
                # Fallback nếu có giá trị role khác phát sinh
                users = users.filter(role=role)
        if district:
            users = users.filter(district=district)
        if search:
            users = users.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        paginator = Paginator(users, 25)
        page = paginator.get_page(request.GET.get('page', 1))

        role_filters = [
            ('admin', 'Admin'),
            ('staff', 'Cán bộ'),
            ('citizen', 'Người dân'),
        ]

        districts_in_db = list(
            User.objects.exclude(district__isnull=True)
            .exclude(district__exact='')
            .values_list('district', flat=True)
            .distinct()
        )
        districts = []
        for d in DA_NANG_DISTRICTS + sorted(set(districts_in_db)):
            if d and d not in districts:
                districts.append(d)

        return render(
            request,
            'accounts/user_list.html',
            {
                'page_obj': page,
                'role_filters': role_filters,
                'districts': districts,
                'page_title': 'Quản lý người dùng',
            },
        )
    except Exception as exc:
        messages.error(request, f'Không thể tải danh sách người dùng: {exc}')
        return render(
            request,
            'accounts/user_list.html',
            {
                'page_obj': None,
                'role_filters': [('admin', 'Admin'), ('staff', 'Cán bộ'), ('citizen', 'Người dân')],
                'districts': DA_NANG_DISTRICTS,
                'page_title': 'Quản lý người dùng',
            },
        )


@login_required
@admin_required
def create_staff_view(request):
    """
    Tạo tài khoản nhân viên (hoặc admin/công dân) theo form riêng.

    Mục tiêu:
    - Đúng UI: chỉ 1 trường mật khẩu, role & quận dạng select.
    - An toàn: bắt lỗi và báo message rõ ràng, tránh làm gián đoạn hệ thống.
    """
    try:
        if request.method == 'POST':
            form = StaffCreateForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data.get('email') or ''
                phone = form.cleaned_data.get('phone') or ''
                password = form.cleaned_data['password']
                role = form.cleaned_data['role']
                district = form.cleaned_data['district']

                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Tên đăng nhập đã tồn tại.')
                else:
                    user = User(
                        username=username,
                        email=email,
                        phone=phone,
                        role=role,
                        district=district,
                    )
                    user.set_password(password)
                    user.save()
                    messages.success(request, f'Đã tạo tài khoản nhân viên: {user.username}')
                    return redirect('accounts:user_list')
        else:
            form = StaffCreateForm(initial={'role': 'staff', 'district': 'Hải Châu'})

        return render(
            request,
            'accounts/create_staff.html',
            {
                'form': form,
                'page_title': 'Tạo tài khoản nhân viên',
            },
        )
    except Exception as exc:
        messages.error(request, f'Không thể tạo tài khoản: {exc}')
        return redirect('accounts:user_list')


@login_required
@admin_required
def toggle_lock_user_view(request, pk):
    """
    Khóa/Mở khóa tài khoản người dùng theo trạng thái hiện tại.

    - Chỉ chấp nhận POST để tránh thao tác ngoài ý muốn.
    - Khi khóa: vô hiệu hóa toàn bộ session hiện tại của user đó.
    """
    try:
        user_obj = get_object_or_404(User, pk=pk)
        if request.method != 'POST':
            messages.error(request, 'Phương thức không hợp lệ.')
            return redirect('accounts:user_list')

        user_obj.is_locked = not bool(user_obj.is_locked)
        if not user_obj.is_locked:
            user_obj.locked_reason = ''
        user_obj.save()

        if user_obj.is_locked:
            UserSession.objects.filter(user=user_obj).update(is_active=False)
            messages.success(request, f'Đã khóa tài khoản {user_obj.username}.')
        else:
            messages.success(request, f'Đã mở khóa tài khoản {user_obj.username}.')

        return redirect('accounts:user_list')
    except Exception as exc:
        messages.error(request, f'Không thể đổi trạng thái khóa: {exc}')
        return redirect('accounts:user_list')


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
    """
    Hiển thị các phiên đăng nhập đang hoạt động của người dùng.

    - Dữ liệu lấy từ `UserSession`.
    - Template sẽ đánh dấu phiên hiện tại dựa trên `request.session.session_key`.
    """
    try:
        sessions = UserSession.objects.filter(user=request.user, is_active=True).order_by('-last_activity')
        return render(
            request,
            'accounts/sessions.html',
            {
                'sessions': sessions,
                'current_session_key': request.session.session_key,
                'page_title': 'Quản lý phiên làm việc',
            },
        )
    except Exception as exc:
        messages.error(request, f'Không thể tải danh sách phiên: {exc}')
        return render(
            request,
            'accounts/sessions.html',
            {'sessions': [], 'current_session_key': request.session.session_key, 'page_title': 'Quản lý phiên làm việc'},
        )


@login_required
def revoke_session_view(request, pk):
    """
    Thu hồi (đăng xuất) một phiên đăng nhập cụ thể.

    Lưu ý: không nên thu hồi phiên hiện tại bằng thao tác này (template sẽ chặn UI),
    tuy nhiên vẫn bắt lỗi để đảm bảo an toàn.
    """
    try:
        session = get_object_or_404(UserSession, pk=pk, user=request.user)
        if request.session.session_key and session.session_key == request.session.session_key:
            messages.info(request, 'Đây là phiên hiện tại, không thể thu hồi bằng thao tác này.')
            return redirect('accounts:sessions')
        session.is_active = False
        session.save()
        messages.success(request, 'Đã thu hồi phiên đăng nhập.')
        return redirect('accounts:sessions')
    except Exception as exc:
        messages.error(request, f'Không thể thu hồi phiên: {exc}')
        return redirect('accounts:sessions')


@login_required
def logout_other_devices_view(request):
    """
    Đăng xuất khỏi tất cả các thiết bị khác, giữ lại phiên hiện tại.

    - Chỉ vô hiệu hóa các session khác trong bảng `UserSession`.
    - Không gọi logout() để tránh đăng xuất người dùng khỏi phiên hiện tại.
    """
    try:
        current_key = request.session.session_key
        if not current_key:
            messages.error(request, 'Không xác định được phiên hiện tại.')
            return redirect('accounts:sessions')
        UserSession.objects.filter(user=request.user, is_active=True).exclude(session_key=current_key).update(is_active=False)
        messages.success(request, 'Đã đăng xuất khỏi tất cả các thiết bị khác.')
        return redirect('accounts:sessions')
    except Exception as exc:
        messages.error(request, f'Không thể đăng xuất khỏi thiết bị khác: {exc}')
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

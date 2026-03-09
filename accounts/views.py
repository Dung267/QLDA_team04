# accounts/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

User = get_user_model()

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "CITIZEN")

        if not username or not email or not password:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return render(request, "accounts/register.html")

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại.")
            return render(request, "accounts/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại.")
            return render(request, "accounts/register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if hasattr(user, "role"):
            user.role = role
        user.save()

        messages.success(request, "Đăng ký thành công. Mời bạn đăng nhập.")
        return redirect("/accounts/login/")

    return render(request, "accounts/register.html")


def login(request):
    if request.user.is_authenticated:
        return redirect("/accounts/profile/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Đăng nhập thành công.")
            return redirect("/accounts/profile/")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")

    return render(request, "accounts/login.html")


@login_required
def update_account(request):
    user = request.user

    if request.method == "POST":
        user.email = request.POST.get("email", user.email)
        if hasattr(user, "phone"):
            user.phone = request.POST.get("phone", getattr(user, "phone", ""))
        if hasattr(user, "address"):
            user.address = request.POST.get("address", getattr(user, "address", ""))
        user.save()
        messages.success(request, "Cập nhật tài khoản thành công.")
        return redirect("/accounts/profile/")

    return render(request, "accounts/update_account.html", {"user_obj": user})


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not request.user.check_password(old_password):
            messages.error(request, "Mật khẩu cũ không đúng.")
            return render(request, "accounts/change_password.html")

        if new_password != confirm_password:
            messages.error(request, "Mật khẩu mới và xác nhận không khớp.")
            return render(request, "accounts/change_password.html")

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Đổi mật khẩu thành công.")
        return redirect("/accounts/profile/")

    return render(request, "accounts/change_password.html")


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})
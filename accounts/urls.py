from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('login-history/', views.login_history_view, name='login_history'),
    path('sessions/', views.active_sessions_view, name='sessions'),
    path('sessions/<int:pk>/revoke/', views.revoke_session_view, name='revoke_session'),
    path('logout-all/', views.logout_all_devices_view, name='logout_all'),
    # Admin
    path('users/', views.user_list_view, name='user_list'),
    path('users/create-staff/', views.create_staff_view, name='create_staff'),
    path('users/<int:pk>/lock/', views.lock_user_view, name='lock_user'),
    path('users/<int:pk>/unlock/', views.unlock_user_view, name='unlock_user'),
    path('users/<int:pk>/delete/', views.delete_user_view, name='delete_user'),
    path('users/<int:pk>/assign-role/', views.assign_role_view, name='assign_role'),
]
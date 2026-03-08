# config/urls.py

from django.contrib import admin
from django.urls import path
from common.views import home  # Thêm import view home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Thêm đường dẫn đến trang chủ
]
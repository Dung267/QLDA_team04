from django.urls import path
from . import core_views

urlpatterns = [
    path('', core_views.dashboard, name='dashboard'),
    path('home/', core_views.home, name='home'),
]

from django.urls import path
from . import views
app_name = 'permits'
urlpatterns = [
    path('', views.PermitListView.as_view(), name='list'),
    path('create/', views.PermitCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PermitDetailView.as_view(), name='detail'),
    path('<int:pk>/submit/', views.permit_submit, name='submit'),
    path('<int:pk>/process/', views.process_permit, name='process'),
    path('stats/', views.permit_stats, name='stats'),
]

from django.urls import path
from . import api_views

urlpatterns = [
    path('summary/', api_views.summary_stats_api, name='api_report_summary'),
    path('monthly/', api_views.monthly_stats_api, name='api_report_monthly'),
    path('area-comparison/', api_views.area_comparison_api, name='api_report_area'),
]

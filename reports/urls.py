from django.urls import path

from . import views


app_name = "reports"

urlpatterns = [
    path("", views.report_summary, name="summary"),
    path("monthly/", views.monthly_report, name="monthly"),
    path("yearly/", views.yearly_report, name="yearly"),
    path("export/excel/", views.export_excel, name="export_excel"),
    path("export/pdf/", views.export_pdf, name="export_pdf"),
    path("export/word/", views.export_word, name="export_word"),
    path("export/monthly/excel/", views.export_monthly_excel, name="export_monthly_excel"),
    path("export/monthly/pdf/", views.export_monthly_pdf, name="export_monthly_pdf"),
    path("export/monthly/word/", views.export_monthly_word, name="export_monthly_word"),
]

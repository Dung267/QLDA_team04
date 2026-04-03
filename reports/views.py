from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import date, timedelta
from .models import Report
from accounts.decorators import staff_required


@login_required
@staff_required
def report_dashboard(request):
    now = timezone.now()
    month_start = now.date().replace(day=1)
    year_start = now.date().replace(month=1, day=1)

    from maintenance.models import MaintenanceRequest
    from infrastructure.models import Road, TrafficLight
    from inventory.models import Material, StockTransaction

    context = {
        'page_title': 'Báo cáo & Thống kê',
        # Bảo trì
        'maintenance_this_month': MaintenanceRequest.objects.filter(created_at__date__gte=month_start).count(),
        'maintenance_completed': MaintenanceRequest.objects.filter(status='completed', completed_at__date__gte=month_start).count(),
        'maintenance_by_type': list(MaintenanceRequest.objects.values('incident_type').annotate(c=Count('id')).order_by('-c')[:5]),
        'maintenance_by_status': list(MaintenanceRequest.objects.values('status').annotate(c=Count('id'))),
        # Hạ tầng
        'roads_by_status': list(Road.objects.values('status').annotate(c=Count('id'))),
        'lights_by_status': list(TrafficLight.objects.values('status').annotate(c=Count('id'))),
        # Vật tư
        'low_stock_count': Material.objects.filter(quantity_in_stock__lte=0).count(),
        # Thời gian
        'now': now,
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@staff_required
def monthly_report(request):
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    start = date(year, month, 1)
    end = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)

    from maintenance.models import MaintenanceRequest
    data = {
        'period': f"Tháng {month:02d}/{year}",
        'total_requests': MaintenanceRequest.objects.filter(created_at__date__range=[start, end]).count(),
        'completed': MaintenanceRequest.objects.filter(status='completed', completed_at__date__range=[start, end]).count(),
        'by_type': list(MaintenanceRequest.objects.filter(created_at__date__range=[start, end]).values('incident_type').annotate(c=Count('id'))),
        'avg_rating': MaintenanceRequest.objects.filter(citizen_rating__isnull=False, completed_at__date__range=[start, end]).aggregate(avg=Avg('citizen_rating'))['avg'],
    }
    return render(request, 'reports/monthly.html', {'data': data, 'year': year, 'month': month, 'page_title': f'Báo cáo tháng {month}/{year}'})


@login_required
@staff_required
def quarterly_report(request):
    year = int(request.GET.get('year', timezone.now().year))
    quarter = int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1))
    q_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
    m_start, m_end = q_months[quarter]
    start = date(year, m_start, 1)
    end = date(year, m_end, 28)

    from maintenance.models import MaintenanceRequest
    data = {
        'period': f"Quý {quarter}/{year}",
        'total_requests': MaintenanceRequest.objects.filter(created_at__date__range=[start, end]).count(),
        'completed': MaintenanceRequest.objects.filter(status='completed', completed_at__date__range=[start, end]).count(),
    }
    return render(request, 'reports/quarterly.html', {'data': data, 'year': year, 'quarter': quarter, 'page_title': f'Báo cáo quý {quarter}/{year}'})


@login_required
@staff_required
def yearly_report(request):
    year = int(request.GET.get('year', timezone.now().year))
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    from maintenance.models import MaintenanceRequest
    data = {
        'period': f"Năm {year}",
        'total_requests': MaintenanceRequest.objects.filter(created_at__date__range=[start, end]).count(),
        'completed': MaintenanceRequest.objects.filter(status='completed', completed_at__date__range=[start, end]).count(),
    }
    return render(request, 'reports/yearly.html', {'data': data, 'year': year, 'page_title': f'Báo cáo năm {year}'})


@login_required
@staff_required
def export_excel(request):
    import openpyxl
    from io import BytesIO
    from maintenance.models import MaintenanceRequest

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Báo cáo sự cố'
    headers = ['ID', 'Tiêu đề', 'Loại sự cố', 'Mức ưu tiên', 'Trạng thái', 'Người báo cáo', 'Ngày tạo']
    ws.append(headers)

    for req in MaintenanceRequest.objects.all()[:1000]:
        ws.append([
            req.pk, req.title, req.get_incident_type_display(),
            req.get_priority_display(), req.get_status_display(),
            req.reported_by.username if req.reported_by else '',
            req.created_at.strftime('%d/%m/%Y %H:%M'),
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    response = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_{timezone.now().strftime("%Y%m%d")}.xlsx"'
    return response


@login_required
@staff_required
def export_pdf(request):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from io import BytesIO

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(100, 800, 'BAO CAO HE THONG HA TANG DO THI')
    c.setFont('Helvetica', 12)
    c.drawString(100, 770, f'Ngay xuat: {timezone.now().strftime("%d/%m/%Y %H:%M")}')

    from maintenance.models import MaintenanceRequest
    y = 740
    c.drawString(100, y, f'Tong so phan anh: {MaintenanceRequest.objects.count()}')
    y -= 20
    c.drawString(100, y, f'Cho xu ly: {MaintenanceRequest.objects.filter(status="pending").count()}')
    y -= 20
    c.drawString(100, y, f'Da hoan thanh: {MaintenanceRequest.objects.filter(status="completed").count()}')
    c.save()

    buf.seek(0)
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response

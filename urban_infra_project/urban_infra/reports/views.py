from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from accounts.decorators import staff_required

@login_required
@staff_required
def report_summary(request):
    from maintenance.models import MaintenanceRequest
    from infrastructure.models import Road, TrafficLight
    from vehicle_inspection.models import Inspection
    now = timezone.now()
    month_start = now.date().replace(day=1)
    stats = {
        'total_incidents': MaintenanceRequest.objects.count(),
        'monthly_incidents': MaintenanceRequest.objects.filter(created_at__date__gte=month_start).count(),
        'completed_incidents': MaintenanceRequest.objects.filter(status='completed').count(),
        'total_roads': Road.objects.count(),
        'total_lights': TrafficLight.objects.count(),
        'total_inspections': Inspection.objects.count(),
        'incidents_by_type': list(MaintenanceRequest.objects.values('incident_type').annotate(count=Count('id'))),
        'incidents_by_status': list(MaintenanceRequest.objects.values('status').annotate(count=Count('id'))),
        'total_cost': float(MaintenanceRequest.objects.aggregate(t=Sum('actual_cost'))['t'] or 0),
        'avg_rating': MaintenanceRequest.objects.filter(citizen_rating__isnull=False).aggregate(avg=Avg('citizen_rating'))['avg'],
    }
    return render(request,'reports/summary.html',{'stats':stats,'page_title':'Báo cáo tổng hợp'})

@login_required
@staff_required
def monthly_report(request):
    from maintenance.models import MaintenanceRequest
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    qs = MaintenanceRequest.objects.filter(created_at__year=year, created_at__month=month)
    stats = {
        'month': month, 'year': year,
        'total': qs.count(),
        'completed': qs.filter(status='completed').count(),
        'by_type': list(qs.values('incident_type').annotate(count=Count('id'))),
        'cost': float(qs.aggregate(t=Sum('actual_cost'))['t'] or 0),
    }
    return render(request,'reports/monthly.html',{'stats':stats,'page_title':f'Báo cáo tháng {month}/{year}'})

@login_required
@staff_required
def yearly_report(request):
    from maintenance.models import MaintenanceRequest
    year = int(request.GET.get('year', timezone.now().year))
    monthly = []
    for m in range(1,13):
        qs = MaintenanceRequest.objects.filter(created_at__year=year, created_at__month=m)
        monthly.append({'month':m,'count':qs.count(),'cost':float(qs.aggregate(t=Sum('actual_cost'))['t'] or 0)})
    return render(request,'reports/yearly.html',{'monthly':monthly,'year':year,'page_title':f'Báo cáo năm {year}'})

@login_required
@staff_required
def export_excel(request):
    import openpyxl
    from maintenance.models import MaintenanceRequest
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Báo cáo sự cố'
    headers = ['STT','Tiêu đề','Loại','Mức độ','Trạng thái','Người báo','Ngày tạo','Ngày HT','Chi phí']
    ws.append(headers)
    for i,r in enumerate(MaintenanceRequest.objects.all(), 1):
        ws.append([
            i, r.title, r.get_incident_type_display(), r.get_priority_display(),
            r.get_status_display(),
            r.reported_by.get_full_name() if r.reported_by else '',
            r.created_at.strftime('%d/%m/%Y') if r.created_at else '',
            r.completed_at.strftime('%d/%m/%Y') if r.completed_at else '',
            float(r.actual_cost),
        ])
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename="bao_cao_su_co.xlsx"'
    wb.save(resp)
    return resp

@login_required
@staff_required
def export_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from maintenance.models import MaintenanceRequest
    resp = HttpResponse(content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="bao_cao.pdf"'
    p = canvas.Canvas(resp, pagesize=A4)
    w, h = A4
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(w/2, h-2*cm, "BAO CAO SU CO HA TANG DO THI")
    p.setFont("Helvetica", 11)
    total = MaintenanceRequest.objects.count()
    completed = MaintenanceRequest.objects.filter(status='completed').count()
    p.drawString(2*cm, h-4*cm, f"Tong so su co: {total}")
    p.drawString(2*cm, h-5*cm, f"Da hoan thanh: {completed}")
    p.drawString(2*cm, h-6*cm, f"Ngay xuat: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    p.showPage()
    p.save()
    return resp

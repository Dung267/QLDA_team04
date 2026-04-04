from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import APIIntegration, WebhookLog
from accounts.decorators import admin_required

@login_required
@admin_required
def integration_list(request):
    integrations = APIIntegration.objects.all()
    return render(request,'integration/list.html',{'integrations':integrations,'page_title':'Tích hợp hệ thống'})

@login_required
@admin_required
def test_integration(request, pk):
    from django.utils import timezone
    integration = APIIntegration.objects.get(pk=pk)
    try:
        import requests
        resp = requests.get(integration.endpoint, timeout=5)
        integration.status = 'active' if resp.status_code<400 else 'error'
        integration.last_sync = timezone.now()
        integration.error_message = '' if resp.status_code<400 else f"HTTP {resp.status_code}"
        integration.save()
        return JsonResponse({'success':True,'status':integration.status})
    except Exception as e:
        integration.status = 'error'
        integration.error_message = str(e)
        integration.save()
        return JsonResponse({'success':False,'error':str(e)})

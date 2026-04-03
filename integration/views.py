from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import APIIntegration, APILog
from accounts.decorators import admin_required


@login_required
@admin_required
def integration_list(request):
    integrations = APIIntegration.objects.all()
    return render(request, 'integration/list.html', {
        'integrations': integrations, 'page_title': 'Tích hợp hệ thống'
    })


@login_required
@admin_required
def integration_test(request, pk):
    integration = get_object_or_404(APIIntegration, pk=pk)
    try:
        import requests
        response = requests.get(integration.base_url, timeout=10)
        integration.status = 'active' if response.ok else 'error'
        integration.save(update_fields=['status'])
        APILog.objects.create(
            integration=integration, method='GET', endpoint=integration.base_url,
            response_status=response.status_code, is_success=response.ok
        )
        return JsonResponse({'success': response.ok, 'status': response.status_code})
    except Exception as e:
        integration.status = 'error'
        integration.save(update_fields=['status'])
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@admin_required
def api_logs(request, pk):
    integration = get_object_or_404(APIIntegration, pk=pk)
    logs = integration.logs.all()[:50]
    return render(request, 'integration/logs.html', {
        'integration': integration, 'logs': logs, 'page_title': f'Logs - {integration.name}'
    })

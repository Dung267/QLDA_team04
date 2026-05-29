from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import APIIntegration, WebhookLog
import requests
import json
from datetime import datetime


@login_required
@require_http_methods(["GET"])
def list_integrations(request):
    """
    Danh sách tích hợp API
    - Hiển thị tất cả integrations
    - Status badge (active, inactive, error)
    - Health check indicator
    - Last sync time
    """
    integrations = APIIntegration.objects.prefetch_related('webhook_logs').order_by('-created_at')
    
    # Calculate stats
    total_count = integrations.count()
    active_count = integrations.filter(status='active').count()
    error_count = integrations.filter(status='error').count()
    
    context = {
        'integrations': integrations,
        'total_count': total_count,
        'active_count': active_count,
        'error_count': error_count,
    }
    return render(request, 'integration/list.html', context)


@staff_member_required
@require_http_methods(["POST"])
def create_integration(request):
    """
    Tạo tích hợp API mới
    - Validate required fields
    - Create APIIntegration record
    - Set initial status as 'inactive'
    """
    name = request.POST.get('name', '').strip()
    endpoint = request.POST.get('endpoint', '').strip()
    api_key = request.POST.get('api_key', '').strip()
    
    if not name:
        messages.error(request, 'Tên tích hợp không được để trống!')
        return redirect('integration:list')
    
    try:
        # Check if name already exists
        if APIIntegration.objects.filter(name=name).exists():
            messages.error(request, f'Tích hợp "{name}" đã tồn tại!')
            return redirect('integration:list')
        
        # Create integration
        integration = APIIntegration.objects.create(
            name=name,
            endpoint=endpoint or '',
            api_key=api_key or '',
            status='inactive'
        )
        
        messages.success(request, f'Tích hợp "{name}" đã được tạo thành công!')
        
    except Exception as e:
        messages.error(request, f'Lỗi tạo tích hợp: {str(e)}')
    
    return redirect('integration:list')


@staff_member_required
@require_http_methods(["POST"])
def update_integration(request, pk):
    """
    Cập nhật tích hợp API
    - Update name, endpoint, api_key, status
    - Validate endpoint URL
    - Don't overwrite api_key if left empty
    """
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    try:
        name = request.POST.get('name', '').strip()
        endpoint = request.POST.get('endpoint', '').strip()
        api_key = request.POST.get('api_key', '').strip()
        status = request.POST.get('status', 'inactive')
        
        if not name:
            messages.error(request, 'Tên tích hợp không được để trống!')
            return redirect('integration:list')
        
        # Check if name is changed and already exists
        if name != integration.name and APIIntegration.objects.filter(name=name).exists():
            messages.error(request, f'Tích hợp "{name}" đã tồn tại!')
            return redirect('integration:list')
        
        # Update fields
        integration.name = name
        integration.endpoint = endpoint
        
        # Only update api_key if provided
        if api_key:
            integration.api_key = api_key
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'error']
        if status in valid_statuses:
            integration.status = status
        
        integration.save()
        
        messages.success(request, f'Tích hợp "{name}" đã được cập nhật!')
        
    except Exception as e:
        messages.error(request, f'Lỗi cập nhật tích hợp: {str(e)}')
    
    return redirect('integration:list')


@staff_member_required
@require_http_methods(["POST"])
def delete_integration(request, pk):
    """
    Xóa tích hợp API
    - Xóa APIIntegration record
    - Cascade delete WebhookLogs
    """
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    try:
        name = integration.name
        integration.delete()
        messages.success(request, f'Tích hợp "{name}" đã được xóa!')
        
    except Exception as e:
        messages.error(request, f'Lỗi xóa tích hợp: {str(e)}')
    
    return redirect('integration:list')


@staff_member_required
@require_http_methods(["POST"])
def test_connection(request, pk):
    """
    Test kết nối API
    - Test endpoint với API key
    - Ghi log result vào WebhookLog
    - Update status và error_message
    - Return JSON response
    """
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    if not integration.endpoint:
        return JsonResponse({
            'success': False,
            'error': 'Endpoint chưa được cấu hình'
        })
    
    try:
        # Prepare headers
        headers = {
            'User-Agent': 'Urban-Infra-System/1.0',
            'Content-Type': 'application/json'
        }
        
        if integration.api_key:
            headers['Authorization'] = f'Bearer {integration.api_key}'
        
        # Make test request
        response = requests.get(
            integration.endpoint,
            headers=headers,
            timeout=10
        )
        
        # Create webhook log
        is_success = 200 <= response.status_code < 300
        
        WebhookLog.objects.create(
            integration=integration,
            event_type='test_connection',
            payload=json.dumps({
                'endpoint': integration.endpoint,
                'request_headers': {k: v for k, v in headers.items() if k != 'Authorization'}
            }),
            response_code=response.status_code,
            is_success=is_success
        )
        
        # Update integration status
        if is_success:
            integration.status = 'active'
            integration.error_message = ''
            integration.last_sync = timezone.now()
        else:
            integration.status = 'error'
            integration.error_message = f'HTTP {response.status_code}: {response.reason}'
        
        integration.save()
        
        return JsonResponse({
            'success': is_success,
            'response_code': response.status_code,
            'message': f'HTTP {response.status_code}: {response.reason}'
        })
        
    except requests.exceptions.Timeout:
        error_msg = 'Request timeout (10s)'
        integration.status = 'error'
        integration.error_message = error_msg
        integration.save()
        
        WebhookLog.objects.create(
            integration=integration,
            event_type='test_connection',
            payload=json.dumps({'error': 'timeout'}),
            is_success=False
        )
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        })
        
    except requests.exceptions.ConnectionError:
        error_msg = 'Không thể kết nối đến endpoint'
        integration.status = 'error'
        integration.error_message = error_msg
        integration.save()
        
        WebhookLog.objects.create(
            integration=integration,
            event_type='test_connection',
            payload=json.dumps({'error': 'connection_error'}),
            is_success=False
        )
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        })
        
    except Exception as e:
        error_msg = str(e)
        integration.status = 'error'
        integration.error_message = error_msg
        integration.save()
        
        WebhookLog.objects.create(
            integration=integration,
            event_type='test_connection',
            payload=json.dumps({'error': error_msg}),
            is_success=False
        )
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        })


@staff_member_required
@require_http_methods(["GET"])
def integration_stats(request):
    """
    Thống kê API integrations
    - Tính toán health metrics
    - Success rate per integration
    - Webhook log statistics
    """
    integrations = APIIntegration.objects.all()
    
    stats = {
        'total': integrations.count(),
        'active': integrations.filter(status='active').count(),
        'inactive': integrations.filter(status='inactive').count(),
        'error': integrations.filter(status='error').count(),
    }
    
    # Calculate success rates
    integration_stats = []
    for integration in integrations:
        logs = integration.webhook_logs.all()
        if logs.exists():
            total_logs = logs.count()
            success_logs = logs.filter(is_success=True).count()
            success_rate = (success_logs / total_logs * 100) if total_logs > 0 else 0
        else:
            success_rate = 0
        
        integration_stats.append({
            'integration': integration,
            'success_rate': f'{success_rate:.1f}%',
            'total_logs': logs.count(),
            'last_log': logs.first(),
        })
    
    context = {
        'stats': stats,
        'integration_stats': integration_stats,
    }
    return render(request, 'integration/stats.html', context)


@staff_member_required
@require_http_methods(["GET"])
def webhook_logs(request, pk):
    """
    Xem chi tiết webhook logs cho một integration
    - Hiển thị danh sách logs
    - Filter by event_type
    - Filter by success/failure
    - Pagination
    """
    integration = get_object_or_404(APIIntegration, pk=pk)
    logs = integration.webhook_logs.all()
    
    # Filter by event type
    event_type = request.GET.get('event_type')
    if event_type:
        logs = logs.filter(event_type=event_type)
    
    # Filter by success
    success_filter = request.GET.get('success')
    if success_filter == 'true':
        logs = logs.filter(is_success=True)
    elif success_filter == 'false':
        logs = logs.filter(is_success=False)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'integration': integration,
        'logs': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'integration/webhook_logs.html', context)


@staff_member_required
@require_http_methods(["POST"])
def trigger_sync(request, pk):
    """
    Trigger manual sync untuk integration
    - Test connection terlebih dahulu
    - Jalankan sync logic (Celery task)
    - Update last_sync timestamp
    """
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    if not integration.endpoint:
        messages.error(request, 'Endpoint chưa được cấu hình!')
        return redirect('integration:list')
    
    try:
        # Test connection first
        headers = {'User-Agent': 'Urban-Infra-System/1.0'}
        if integration.api_key:
            headers['Authorization'] = f'Bearer {integration.api_key}'
        
        response = requests.get(
            integration.endpoint,
            headers=headers,
            timeout=10
        )
        
        if 200 <= response.status_code < 300:
            # Update sync timestamp
            integration.last_sync = timezone.now()
            integration.status = 'active'
            integration.error_message = ''
            integration.save()
            
            messages.success(request, f'Đồng bộ "{integration.name}" thành công!')
        else:
            integration.status = 'error'
            integration.error_message = f'HTTP {response.status_code}'
            integration.save()
            
            messages.error(request, f'Lỗi đồng bộ: HTTP {response.status_code}')
        
    except Exception as e:
        integration.status = 'error'
        integration.error_message = str(e)
        integration.save()
        
        messages.error(request, f'Lỗi đồng bộ: {str(e)}')
    
    return redirect('integration:list')
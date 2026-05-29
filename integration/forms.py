from django import forms
from .models import APIIntegration, WebhookLog


class APIIntegrationForm(forms.ModelForm):
    """Form tạo/chỉnh sửa API Integration"""
    
    class Meta:
        model = APIIntegration
        fields = ['name', 'api_key', 'endpoint', 'status']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Google Drive, AWS S3, Slack...',
                'maxlength': '100',
            }),
            'endpoint': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://api.example.com/v1',
            }),
            'api_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'sk_live_... hoặc token...',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        
        labels = {
            'name': 'Tên tích hợp',
            'api_key': 'API Key',
            'endpoint': 'Endpoint URL',
            'status': 'Trạng thái',
        }
    
    def clean_name(self):
        """Validate name is unique"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise forms.ValidationError('Tên tích hợp không được để trống!')
        
        # Check uniqueness (exclude current instance if editing)
        query = APIIntegration.objects.filter(name=name)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError(f'Tích hợp "{name}" đã tồn tại!')
        
        return name
    
    def clean_endpoint(self):
        """Validate endpoint format"""
        endpoint = self.cleaned_data.get('endpoint', '').strip()
        
        if endpoint:
            # Verify it's a valid URL
            if not (endpoint.startswith('http://') or endpoint.startswith('https://')):
                raise forms.ValidationError('Endpoint phải bắt đầu bằng http:// hoặc https://')
        
        return endpoint
    
    def clean_api_key(self):
        """Validate API key format"""
        api_key = self.cleaned_data.get('api_key', '').strip()
        
        if api_key and len(api_key) < 10:
            raise forms.ValidationError('API Key quá ngắn (tối thiểu 10 ký tự)')
        
        return api_key


class WebhookLogFilterForm(forms.Form):
    """Form filter webhook logs"""
    
    EVENT_TYPE_CHOICES = [
        ('', '-- Tất cả event --'),
        ('test_connection', 'Test Connection'),
        ('sync', 'Sync'),
        ('webhook_received', 'Webhook Received'),
    ]
    
    SUCCESS_CHOICES = [
        ('', '-- Tất cả --'),
        ('true', 'Thành công'),
        ('false', 'Thất bại'),
    ]
    
    event_type = forms.ChoiceField(
        label='Event Type',
        choices=EVENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    success = forms.ChoiceField(
        label='Status',
        choices=SUCCESS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
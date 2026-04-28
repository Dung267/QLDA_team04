from django import forms
from .models import BackupConfig, BackupRecord


class BackupConfigForm(forms.ModelForm):
    """Form cấu hình backup"""
    
    class Meta:
        model = BackupConfig
        fields = ['is_auto', 'frequency', 'time_of_day', 'max_backups', 'include_media', 'compress', 'encrypt', 'upload_to_cloud']
        
        widgets = {
            'is_auto': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
            }),
            'time_of_day': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'max_backups': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100',
            }),
            'include_media': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'compress': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'encrypt': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'upload_to_cloud': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        
        labels = {
            'is_auto': 'Backup tự động',
            'frequency': 'Tần suất',
            'time_of_day': 'Giờ backup',
            'max_backups': 'Số lượng backup tối đa',
            'include_media': 'Bao gồm media files',
            'compress': 'Nén file backup',
            'encrypt': 'Mã hóa backup',
            'upload_to_cloud': 'Upload lên cloud',
        }


class CreateBackupForm(forms.Form):
    """Form tạo backup"""
    
    BACKUP_TYPE_CHOICES = [
        ('full', 'Đầy đủ (Full) - Sao lưu toàn bộ dữ liệu'),
        ('incremental', 'Tăng cộng (Incremental) - Chỉ dữ liệu mới/thay đổi kể từ backup cuối'),
        ('differential', 'Khác biệt (Differential) - Dữ liệu mới/thay đổi kể từ backup Full cuối'),
    ]
    
    backup_type = forms.ChoiceField(
        label='Loại Backup',
        choices=BACKUP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        initial='full',
        help_text='Chọn loại backup phù hợp'
    )


class RestoreForm(forms.Form):
    """Form khôi phục backup"""
    
    confirm = forms.BooleanField(
        label='Tôi đã hiểu và chấp nhận rủi ro',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    note = forms.CharField(
        label='Ghi chú (tùy chọn)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Nhập ghi chú về lý do khôi phục...'
        })
    )
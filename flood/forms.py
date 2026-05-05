from django import forms
from .models import FloodAlert


class FloodAlertForm(forms.ModelForm):
    """
    Form tạo / cập nhật cảnh báo ngập lụt.

    Không bao gồm các field tự động hoặc chỉ dùng nội bộ:
        created_by, created_at, updated_at, resolved_at
    is_sent_sms và rescue_teams_notified được giữ lại để cán bộ
    có thể đánh dấu khi phát lệnh.
    """

    class Meta:
        model = FloodAlert
        exclude = ['created_by', 'created_at', 'updated_at', 'resolved_at']

        widgets = {
            # Bắt buộc
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Ngập lụt nghiêm trọng khu vực Hải Châu',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Diễn biến, nguyên nhân, phạm vi ảnh hưởng...',
            }),
            'level': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'area_type': forms.Select(attrs={'class': 'form-select'}),
            'area_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Phường Hải Châu 1, Quận Hải Châu',
                'maxlength': 200,
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '16.047079',
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '108.206230',
            }),
            'water_level_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 999,
                'placeholder': '50',
            }),

            # Tuỳ chọn – hướng dẫn ứng phó
            'safe_routes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Liệt kê các tuyến đường có thể di chuyển an toàn...',
            }),
            'evacuation_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hướng dẫn di chuyển, tránh các khu vực nguy hiểm...',
            }),
            'shelter_locations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Các trường học, nhà văn hóa, điểm tập kết an toàn...',
            }),

            # Kênh thông báo
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_sent_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rescue_teams_notified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Đánh dấu các trường bắt buộc
        required_fields = ['title', 'description', 'level', 'area_type', 'area_name']
        for field in required_fields:
            self.fields[field].required = True

        # latitude, longitude, water_level_cm: bắt buộc theo thiết kế DB
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['water_level_cm'].required = True

        # Các trường không bắt buộc
        optional = ['safe_routes', 'evacuation_info', 'shelter_locations',
                    'is_sent_sms', 'rescue_teams_notified', 'is_active']
        for field in optional:
            self.fields[field].required = False
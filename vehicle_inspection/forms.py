from datetime import datetime, time
from django import forms
from django.utils import timezone
from .models import Vehicle, Inspection, InspectionCenter


class VehicleForm(forms.ModelForm):
    """Form tạo/chỉnh sửa phương tiện"""

    class Meta:
        model = Vehicle
        fields = [
            'license_plate',
            'vehicle_type',
            'brand',
            'model',
            'color',
            'year',
            'chassis_number',
            'engine_number',
        ]
        widgets = {
            'license_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: 43A-123.45',
                'maxlength': '20',
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Toyota, Honda, Ford...',
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Vios, Accord, Ranger...',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Trắng, Đen, Đỏ...',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2020',
                'min': '1990',
                'max': str(timezone.localdate().year),
            }),
            'chassis_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số khung xe',
            }),
            'engine_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số máy',
            }),
        }
        labels = {
            'license_plate': 'Biển số xe',
            'vehicle_type': 'Loại xe',
            'brand': 'Hãng xe',
            'model': 'Model',
            'color': 'Màu sắc',
            'year': 'Năm sản xuất',
            'chassis_number': 'Số khung',
            'engine_number': 'Số máy',
        }

    def clean_license_plate(self):
        """Validate biển số xe"""
        license_plate = self.cleaned_data.get('license_plate', '').strip().upper()
        if not license_plate:
            raise forms.ValidationError('Biển số xe không được để trống.')
        if Vehicle.objects.filter(license_plate=license_plate).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Biển số xe này đã tồn tại.')
        return license_plate

    def clean_year(self):
        """Validate năm sản xuất"""
        year = self.cleaned_data.get('year')
        if year:
            current_year = timezone.localdate().year
            if year < 1990 or year > current_year:
                raise forms.ValidationError(f'Năm sản xuất phải từ 1990 đến {current_year}.')
        return year

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.license_plate = self.cleaned_data['license_plate'].upper()
        if commit:
            instance.save()
        return instance


class ScheduleInspectionForm(forms.ModelForm):
    """Form đặt lịch đăng kiểm (cho chủ xe)
    - Chỉ hiển thị: Vehicle, Center, Scheduled Date
    - KHÔNG hiển thị: Fee (cán bộ sẽ nhập sau)
    """
    scheduled_date = forms.DateField(
        label='Ngày hẹn',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )

    class Meta:
        model = Inspection
        fields = ['vehicle', 'center', 'scheduled_date']
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'form-select',
            }),
            'center': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'vehicle': 'Phương tiện',
            'center': 'Trung tâm đăng kiểm',
            'scheduled_date': 'Ngày hẹn',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter: Chỉ hiển thị xe của user hiện tại
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(
                owner=user,
                is_active=True
            ).order_by('license_plate')
        
        # Filter: Chỉ hiển thị trung tâm hoạt động
        self.fields['center'].queryset = InspectionCenter.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Set min date
        min_date = timezone.localdate()
        self.fields['scheduled_date'].widget.attrs['min'] = min_date.isoformat()

    def clean_scheduled_date(self):
        """Validate ngày hẹn phải trong tương lai"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.localdate():
            raise forms.ValidationError('Ngày hẹn không được trong quá khứ.')
        return scheduled_date

    def save(self, commit=True):
        """Convert DateField thành DateTimeField lúc 8:00 sáng"""
        instance = super().save(commit=False)
        selected_date = self.cleaned_data['scheduled_date']
        
        # Combine date với time 8:00 AM
        schedule_dt = datetime.combine(selected_date, time(hour=8, minute=0))
        
        # Make timezone aware
        if timezone.is_naive(schedule_dt):
            schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        
        instance.scheduled_date = schedule_dt
        instance.status = 'pending'
        
        if commit:
            instance.save()
        return instance


class InspectionResultForm(forms.ModelForm):
    """Form cập nhật kết quả đăng kiểm (cho cán bộ)
    - Cập nhật: Status, Defects, Repair Required, Certificate Number, Fee, Valid Until
    """

    class Meta:
        model = Inspection
        fields = [
            'status',
            'technical_notes',
            'defects',
            'repair_required',
            'repair_result',
            'certificate_number',
            'valid_until',
            'fee',
            'is_fee_paid',
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'technical_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ghi chú kỹ thuật...',
            }),
            'defects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Liệt kê các lỗi phát hiện...',
            }),
            'repair_required': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Yêu cầu sửa chữa...',
            }),
            'repair_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Kết quả sửa chữa...',
            }),
            'certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: 43-ABC-12345',
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '340000',
                'min': '0',
            }),
            'is_fee_paid': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'status': 'Trạng thái',
            'technical_notes': 'Ghi chú kỹ thuật',
            'defects': 'Lỗi phát hiện',
            'repair_required': 'Yêu cầu sửa chữa',
            'repair_result': 'Kết quả sửa chữa',
            'certificate_number': 'Số giấy chứng nhận',
            'valid_until': 'Hiệu lực đến',
            'fee': 'Phí đăng kiểm (VNĐ)',
            'is_fee_paid': 'Đã thanh toán',
        }

    def clean(self):
        """Validate logic chung"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        certificate_number = cleaned_data.get('certificate_number')
        valid_until = cleaned_data.get('valid_until')

        # Nếu đạt thì phải có số giấy chứng nhận
        if status == 'passed' and not certificate_number:
            raise forms.ValidationError('Nếu kết quả là "Đạt" thì phải nhập số giấy chứng nhận.')

        # Nếu đạt thì phải có ngày hiệu lực
        if status == 'passed' and not valid_until:
            raise forms.ValidationError('Nếu kết quả là "Đạt" thì phải nhập ngày hiệu lực.')

        return cleaned_data

    def clean_valid_until(self):
        """Validate ngày hiệu lực phải trong tương lai"""
        valid_until = self.cleaned_data.get('valid_until')
        if valid_until and valid_until <= timezone.localdate():
            raise forms.ValidationError('Ngày hiệu lực phải lớn hơn ngày hôm nay.')
        return valid_until

    def clean_fee(self):
        """Validate phí phải >= 0"""
        fee = self.cleaned_data.get('fee')
        if fee is not None and fee < 0:
            raise forms.ValidationError('Phí phải lớn hơn 0.')
        return fee


class PaymentForm(forms.Form):
    """Form thanh toán phí (cho chủ xe)
    - Chỉ là confirmation form
    """
    confirm = forms.BooleanField(
        label='Tôi xác nhận thanh toán phí đăng kiểm',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
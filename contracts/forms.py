from django import forms
from .models import Contract, Tender, Contractor


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        # created_by, approved_by, created_at, updated_at do view/admin set — không hiện trong form
        exclude = ['created_by', 'approved_by', 'created_at', 'updated_at']
        widgets = {
            # Thông tin cơ bản
            'contract_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'VD: HĐ-2026-001',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Tiêu đề hợp đồng...',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
            'progress_percent': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': 0,
                'max': 100,
                'step': 5,
            }),
            # Nhà thầu
            'contractor': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
            # Tài chính
            'value': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': 0,
                'step': 1000000,
                'placeholder': '0',
            }),
            'guaranty': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': 0,
                'step': 1000000,
                'placeholder': '0',
            }),
            # Thời gian
            'start_date': forms.DateInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
            }),
            # Nội dung
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3,
                'placeholder': 'Mô tả công việc, phạm vi hợp đồng...',
            }),
            'terms': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 5,
                'placeholder': 'Điều khoản thanh toán, bảo hành, phạt vi phạm...',
            }),
            # File
            'document': forms.FileInput(attrs={
                'class': 'form-control form-control-sm',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end <= start:
            self.add_error('end_date', 'Ngày kết thúc phải sau ngày bắt đầu.')
        progress = cleaned_data.get('progress_percent')
        if progress is not None and not (0 <= progress <= 100):
            self.add_error('progress_percent', 'Tiến độ phải từ 0 đến 100.')
        return cleaned_data


class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        # created_by, created_at do view set
        fields = ['title', 'description', 'budget', 'deadline', 'status', 'awarded_to', 'result_contract']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'VD: Gói thầu sửa chữa đường Lê Duẩn',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 4,
                'placeholder': 'Mô tả phạm vi công việc, yêu cầu kỹ thuật...',
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': 0,
                'step': 1000000,
                'placeholder': '0',
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'datetime-local',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
            # FK nullable — chỉ hiện khi status='awarded'
            'awarded_to': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
            'result_contract': forms.Select(attrs={
                'class': 'form-select form-select-sm',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        awarded_to = cleaned_data.get('awarded_to')
        # Nếu đã trao thầu thì phải chọn nhà thầu
        if status == 'awarded' and not awarded_to:
            self.add_error('awarded_to', 'Vui lòng chọn nhà thầu trúng thầu.')
        return cleaned_data
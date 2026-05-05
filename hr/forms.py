from django import forms
from .models import WorkAssignment, LeaveRequest, Training, Employee


class WorkAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkAssignment
        fields = ['employee', 'title', 'description', 'due_date', 'status', 'completion_note']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Kiểm tra đèn giao thông tuyến Trần Phú'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # Choices khớp model: todo / in_progress / done / cancelled
            'status': forms.Select(
                attrs={'class': 'form-select'},
                choices=WorkAssignment.STATUS_CHOICES,
            ),
            'completion_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        # Không include 'employee' – view tự set
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                            'placeholder': 'Mô tả rõ lý do nghỉ phép...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.')
        return cleaned_data


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['title', 'description', 'trainer', 'start_date', 'end_date',
                  'participants', 'certificate_required']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'VD: Đào tạo an toàn lao động 2025'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'trainer': forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'Tên giảng viên / đơn vị đào tạo'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'certificate_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.')
        return cleaned_data
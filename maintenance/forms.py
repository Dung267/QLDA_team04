from datetime import timedelta
from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from infrastructure.models import Infrastructure, Road

from .models import MaintenanceRequest, MaintenanceComment, MaintenanceSchedule


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'incident_type', 'priority', 'address',
                  'latitude', 'longitude', 'road', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'road': forms.Select(attrs={'class': 'form-select'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaintenanceCommentForm(forms.ModelForm):
    class Meta:
        model = MaintenanceComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nhập bình luận...'}),
        }


class MaintenanceScheduleForm(forms.ModelForm):
    """Form lập/cập nhật lịch bảo trì theo yêu cầu nghiệp vụ UI."""

    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ]

    item_name = forms.CharField(
        label='Tên hạng mục',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên hạng mục bảo trì'}),
    )
    infrastructure = forms.ChoiceField(
        label='Hạ tầng/Tuyến đường',
        choices=(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    infra_type = forms.ChoiceField(
        label='Phân loại',
        choices=(
            ('road', 'Tuyến đường'),
            ('infra', 'Hạ tầng'),
        ),
        initial='road',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    assigned_to = forms.ModelChoiceField(
        label='Người phụ trách',
        queryset=get_user_model().objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    start_date = forms.DateField(
        label='Ngày bắt đầu',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    end_date = forms.DateField(
        label='Ngày kết thúc',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    cost = forms.DecimalField(
        label='Chi phí dự kiến',
        max_digits=15,
        decimal_places=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '0', 'step': '1000'}),
    )
    estimated_days = forms.IntegerField(
        label='Số ngày thực hiện',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'min': '1', 'step': '1'}),
    )
    priority = forms.ChoiceField(
        label='Độ ưu tiên',
        choices=PRIORITY_CHOICES,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = MaintenanceSchedule
        fields = ['status', 'description']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mô tả chi tiết công việc'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        selected_type = 'road'
        if self.is_bound:
            selected_type = self.data.get('infra_type') or 'road'

        self.fields['infrastructure'].choices = self._build_infrastructure_choices(selected_type)
        self.fields['assigned_to'].queryset = self._get_technician_queryset()

        if self.instance and self.instance.pk:
            self.initial['item_name'] = self.instance.title
            self.initial['cost'] = self.instance.estimated_cost
            self.initial['start_date'] = self.instance.scheduled_date
            self.initial['estimated_days'] = self.instance.period_days or 1

            meta = self._extract_meta(self.instance.description)
            self.initial['priority'] = meta.get('priority', 'medium')
            self.initial['end_date'] = meta.get('end_date') or (
                self.instance.scheduled_date + timedelta(days=max((self.instance.period_days or 1) - 1, 0))
            )
            self.initial['description'] = meta.get('plain_description', self.instance.description or '')

            if self.instance.road_id:
                self.initial['infra_type'] = 'road'
                self.initial['infrastructure'] = str(self.instance.road_id)
            elif self.instance.infrastructure_id:
                self.initial['infra_type'] = 'infra'
                self.initial['infrastructure'] = str(self.instance.infrastructure_id)

            if not self.is_bound:
                selected_type = self.initial.get('infra_type') or 'road'
                self.fields['infrastructure'].choices = self._build_infrastructure_choices(selected_type)

            first_assignee = self.instance.assigned_to.first()
            if first_assignee:
                self.initial['assigned_to'] = first_assignee.pk

        if self.is_bound:
            for name, field in self.fields.items():
                css_class = field.widget.attrs.get('class', '')
                if self.errors.get(name) and 'is-invalid' not in css_class:
                    field.widget.attrs['class'] = f"{css_class} is-invalid".strip()

    def _build_infrastructure_choices(self, infra_type):
        if infra_type == 'infra':
            infrastructures = Infrastructure.objects.order_by('name').values_list('id', 'name')
            if not infrastructures:
                return [('', '--- Chưa có dữ liệu hạ tầng ---')]
            return [('', '--- Chọn hạ tầng ---')] + [(str(pk), name) for pk, name in infrastructures]

        roads = Road.objects.order_by('name').values_list('id', 'name')
        if not roads:
            return [('', '--- Chưa có dữ liệu tuyến đường ---')]
        return [('', '--- Chọn tuyến đường ---')] + [(str(pk), name) for pk, name in roads]

    def _get_technician_queryset(self):
        user_model = get_user_model()
        qs = user_model.objects.filter(is_active=True)
        if hasattr(user_model, 'is_technician'):
            return qs.filter(is_technician=True).order_by('first_name', 'last_name', 'username')

        role_filter = Q()
        has_role_field = hasattr(user_model, 'role')
        if hasattr(user_model, 'role'):
            role_filter |= Q(role='staff')

        group_filter = Q(groups__name__iexact='Nhân viên kỹ thuật') | Q(groups__name__iexact='Technician')
        if has_role_field:
            qs = qs.filter(role_filter | group_filter)
        else:
            qs = qs.filter(group_filter)

        return qs.distinct().order_by('first_name', 'last_name', 'username')

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost is None:
            raise forms.ValidationError('Vui lòng nhập chi phí dự kiến.')
        if cost <= Decimal('0'):
            raise forms.ValidationError('Chi phí phải lớn hơn 0.')
        return cost

    def clean_estimated_days(self):
        estimated_days = self.cleaned_data.get('estimated_days')
        if estimated_days is None:
            raise forms.ValidationError('Vui lòng nhập số ngày dự kiến.')
        if estimated_days <= 0:
            raise forms.ValidationError('Số ngày dự kiến phải là số nguyên lớn hơn 0.')
        return estimated_days

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        infra_type = cleaned_data.get('infra_type')
        infrastructure = cleaned_data.get('infrastructure')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.')

        if infra_type == 'infra' and not Infrastructure.objects.exists():
            self.add_error('infrastructure', 'Chưa có dữ liệu hạ tầng. Vui lòng tạo hạ tầng trước khi lập lịch.')
            return cleaned_data

        if infra_type == 'road' and not Road.objects.exists():
            self.add_error('infrastructure', 'Chưa có dữ liệu tuyến đường. Vui lòng tạo tuyến đường trước khi lập lịch.')
            return cleaned_data

        if not infrastructure:
            if infra_type == 'infra':
                self.add_error('infrastructure', 'Vui lòng chọn hạ tầng.')
            else:
                self.add_error('infrastructure', 'Vui lòng chọn tuyến đường.')

        return cleaned_data

    def _extract_meta(self, raw_description):
        raw_description = raw_description or ''
        lines = raw_description.splitlines()
        plain_lines = []
        meta = {}

        for line in lines:
            if line.startswith('[META_PRIORITY]='):
                meta['priority'] = line.split('=', 1)[1].strip()
                continue
            if line.startswith('[META_END_DATE]='):
                value = line.split('=', 1)[1].strip()
                try:
                    meta['end_date'] = forms.DateField().to_python(value)
                except forms.ValidationError:
                    meta['end_date'] = None
                continue
            plain_lines.append(line)

        while plain_lines and not plain_lines[-1].strip():
            plain_lines.pop()

        meta['plain_description'] = '\n'.join(plain_lines).strip()
        return meta

    def save(self, commit=True):
        schedule = super().save(commit=False)

        selected_infrastructure = self.cleaned_data.get('infrastructure')
        infra_type = self.cleaned_data.get('infra_type')
        if selected_infrastructure and infra_type == 'road':
            schedule.road_id = int(selected_infrastructure)
            schedule.infrastructure = None
        elif selected_infrastructure and infra_type == 'infra':
            schedule.infrastructure_id = int(selected_infrastructure)
            schedule.road = None
        else:
            schedule.road = None
            schedule.infrastructure = None

        schedule.title = self.cleaned_data.get('item_name', '').strip()
        schedule.scheduled_date = self.cleaned_data.get('start_date')
        schedule.estimated_cost = self.cleaned_data.get('cost')
        schedule.period_days = self.cleaned_data.get('estimated_days')

        base_description = (self.cleaned_data.get('description') or '').strip()
        priority = self.cleaned_data.get('priority') or 'medium'
        end_date = self.cleaned_data.get('end_date')
        meta_lines = [
            f'[META_PRIORITY]={priority}',
            f'[META_END_DATE]={end_date.isoformat()}' if end_date else '',
        ]
        meta_text = '\n'.join([line for line in meta_lines if line])
        schedule.description = f"{base_description}\n\n{meta_text}".strip() if meta_text else base_description

        assigned_user = self.cleaned_data.get('assigned_to')

        if commit:
            schedule.save()
            if assigned_user:
                schedule.assigned_to.set([assigned_user])
            else:
                schedule.assigned_to.clear()
        else:
            self._pending_assigned_user = assigned_user

        return schedule

    def save_m2m(self):
        super().save_m2m()
        if hasattr(self, '_pending_assigned_user') and self.instance.pk:
            if self._pending_assigned_user:
                self.instance.assigned_to.set([self._pending_assigned_user])
            else:
                self.instance.assigned_to.clear()

from datetime import datetime, time

from django import forms
from django.utils import timezone

from .models import Vehicle, Inspection, InspectionCenter

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "license_plate",
            "vehicle_type",
            "brand",
            "model",
            "color",
            "year",
            "chassis_number",
            "engine_number",
        ]
        widgets = {
            "license_plate": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "VD: 43A-123.45",
                }
            ),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "brand": forms.TextInput(attrs={"class": "form-control", "placeholder": "Toyota"}),
            "model": forms.TextInput(attrs={"class": "form-control", "placeholder": "Vios"}),
            "color": forms.TextInput(attrs={"class": "form-control", "placeholder": "Trang"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2021"}),
            "chassis_number": forms.TextInput(attrs={"class": "form-control"}),
            "engine_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class ScheduleForm(forms.ModelForm):
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    class Meta:
        model = Inspection
        fields = ["vehicle", "center", "scheduled_date", "fee"]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "center": forms.Select(attrs={"class": "form-select"}),
            "fee": forms.NumberInput(attrs={"class": "form-control", "placeholder": "340000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["center"].queryset = InspectionCenter.objects.filter(is_active=True)

    def clean_scheduled_date(self):
        schedule_date = self.cleaned_data["scheduled_date"]
        if schedule_date < timezone.localdate():
            raise forms.ValidationError("Ngay hen dang kiem khong duoc trong qua khu.")
        return schedule_date

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_date = self.cleaned_data["scheduled_date"]
        schedule_dt = datetime.combine(selected_date, time(hour=8, minute=0))
        if timezone.is_naive(schedule_dt):
            schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        instance.scheduled_date = schedule_dt
        if commit:
            instance.save()
        return instance


InspectionForm = ScheduleForm

class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['vehicle','center','scheduled_date','fee']
        widgets = {
            'vehicle': forms.Select(attrs={'class':'form-select'}),
            'center': forms.Select(attrs={'class':'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fee': forms.NumberInput(attrs={'class':'form-control'}),
        }

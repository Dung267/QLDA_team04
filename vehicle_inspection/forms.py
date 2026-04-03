from django import forms
from .models import Vehicle, Inspection


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['owner', 'is_active', 'created_at']
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InspectionBookingForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['center', 'scheduled_date']
        widgets = {
            'center': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

from django import forms
from .models import Road, Pothole, TrafficLight, Infrastructure


class RoadForm(forms.ModelForm):
    class Meta:
        model = Road
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'quality_score': forms.Select(attrs={'class': 'form-select'}),
            'length_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width_m': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'lanes': forms.NumberInput(attrs={'class': 'form-control'}),
            'built_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'last_repaired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'traffic_density': forms.Select(attrs={'class': 'form-select'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'managing_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'start_point': forms.TextInput(attrs={'class': 'form-control'}),
            'end_point': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PotholeForm(forms.ModelForm):
    class Meta:
        model = Pothole
        exclude = ['road', 'reported_by', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_repaired': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'repaired_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class TrafficLightForm(forms.ModelForm):
    class Meta:
        model = TrafficLight
        exclude = ['created_at', 'updated_at']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'road': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'installed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'managing_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'last_bulb_change': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'operating_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InfrastructureForm(forms.ModelForm):
    class Meta:
        model = Infrastructure
        exclude = ['created_at', 'updated_at']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['name', 'code', 'managing_unit']}
from django import forms
from .models import FloodAlert, DisasterAlert


class FloodAlertForm(forms.ModelForm):
    class Meta:
        model = FloodAlert
        exclude = ['created_by', 'created_at', 'updated_at', 'resolved_at']
        widgets = {
            'area_name': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'water_level_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'safe_routes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'evacuation_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'shelter_locations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DisasterAlertForm(forms.ModelForm):
    class Meta:
        model = DisasterAlert
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['title', 'affected_areas']}

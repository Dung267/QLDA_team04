from django import forms
from .models import Vehicle, Inspection

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['owner','is_active','created_at']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in
                   ['license_plate','brand','model','color','chassis_number','engine_number']}

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

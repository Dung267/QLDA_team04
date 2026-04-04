from django import forms
from .models import ConstructionPermit
class PermitForm(forms.ModelForm):
    class Meta:
        model = ConstructionPermit
        fields = ['title','description','contractor_name','location','latitude','longitude','start_date','end_date','impact_assessment']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'contractor_name': forms.TextInput(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'class':'form-control'}),
            'latitude': forms.NumberInput(attrs={'class':'form-control','step':'0.000001'}),
            'longitude': forms.NumberInput(attrs={'class':'form-control','step':'0.000001'}),
            'start_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'end_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'impact_assessment': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

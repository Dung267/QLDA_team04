from django import forms
from .models import Contract, Tender

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        exclude = ['created_by','created_at','updated_at','approved_by']
        widgets = {
            'start_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'end_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'terms': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        exclude = ['created_by','created_at','awarded_to','result_contract']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

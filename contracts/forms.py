from django import forms
from .models import Contract, Tender, Contractor


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        exclude = ['created_by', 'created_at', 'updated_at']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['contract_number', 'title']}


class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        exclude = ['published_by', 'created_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        exclude = []
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['name', 'tax_code', 'phone', 'email']}

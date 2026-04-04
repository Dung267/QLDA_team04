from django import forms
from .models import StockTransaction

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['material','transaction_type','quantity','unit_price','reason','invoice_number','maintenance_request']
        widgets = {f: forms.Select(attrs={'class':'form-select'}) if f in ['material','transaction_type','maintenance_request'] else forms.TextInput(attrs={'class':'form-control'}) for f in ['material','transaction_type','quantity','unit_price','reason','invoice_number','maintenance_request']}

from django import forms
from .models import FloodAlert

class FloodAlertForm(forms.ModelForm):
    class Meta:
        model = FloodAlert
        exclude = ['created_by','created_at','updated_at','resolved_at','is_sent_sms','rescue_teams_notified']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['title','area_name']}

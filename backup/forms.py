from django import forms
from .models import BackupConfig


class BackupConfigForm(forms.ModelForm):
    class Meta:
        model = BackupConfig
        exclude = ["created_by", "created_at"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "frequency": forms.Select(attrs={"class":"form-select"}),
            "backup_time": forms.TimeInput(attrs={"class":"form-control","type":"time"}),
            "max_backups": forms.NumberInput(attrs={"class":"form-control"}),
            "include_media": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "include_db": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "compress": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "encrypt": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "upload_to_cloud": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

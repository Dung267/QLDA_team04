from django import forms
from .models import Document
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = ['uploaded_by','created_at','updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-select'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'file': forms.FileInput(attrs={'class':'form-control'}),
            'version': forms.TextInput(attrs={'class':'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

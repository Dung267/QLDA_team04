from django import forms
from .models import SystemFeedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = SystemFeedback
        fields = ['title', 'category', 'content', 'rating', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

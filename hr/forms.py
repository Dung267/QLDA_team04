from django import forms
from .models import WorkAssignment, LeaveRequest

class WorkAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkAssignment
        fields = ['employee','title','description','due_date','status']
        widgets = {
            'employee': forms.Select(attrs={'class':'form-select'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'due_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'status': forms.Select(attrs={'class':'form-select'}),
        }

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type','start_date','end_date','reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class':'form-select'}),
            'start_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'end_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'reason': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

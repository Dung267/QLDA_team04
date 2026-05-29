from django import forms
from .models import SystemFeedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = SystemFeedback
        fields = ['category', 'content', 'rating', 'is_anonymous']
        widgets = {
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Giao thông, Chiếu sáng, Thoát nước tại quận Hải Châu',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Góp ý về hạ tầng tại quận Hải Châu, Đà Nẵng...',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'category': 'Phân loại phản hồi',
            'content': 'Nội dung phản hồi',
            'rating': 'Đánh giá hệ thống (1-5 sao)',
            'is_anonymous': 'Gửi ẩn danh',
        }

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if not 1 <= rating <= 5:
            raise forms.ValidationError('Điểm đánh giá phải nằm trong khoảng từ 1 đến 5.')
        return rating

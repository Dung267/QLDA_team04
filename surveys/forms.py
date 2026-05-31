from django import forms

from .models import Survey, SurveyResponse


class SurveyCreateForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ["title", "description", "deadline", "is_active"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ví dụ: Khảo sát hài lòng về chỉnh trang Hải Châu",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Mô tả ngắn về nội dung khảo sát, ví dụ: tuyến phố, công viên, hạ tầng...",
                }
            ),
            "deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "title": "Tiêu đề",
            "description": "Mô tả",
            "deadline": "Hạn khảo sát",
            "is_active": "Kích hoạt ngay",
        }


class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = ["satisfaction_score", "comments"]
        widgets = {
            "satisfaction_score": forms.HiddenInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "step": 1,
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Ví dụ: Góp ý về Cầu Rồng, tuyến phố Bạch Đằng, công viên Biển Đông...",
                }
            ),
        }
        labels = {
            "satisfaction_score": "Mức đánh giá (1-5 sao)",
            "comments": "Nhận xét thêm",
        }

    def clean_satisfaction_score(self):
        satisfaction_score = self.cleaned_data["satisfaction_score"]
        if satisfaction_score is None or not 1 <= satisfaction_score <= 5:
            raise forms.ValidationError("Điểm đánh giá phải nằm trong khoảng từ 1 đến 5.")
        return satisfaction_score
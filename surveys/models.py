from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Survey(models.Model):
    title = models.CharField("Tiêu đề khảo sát", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang hoạt động", default=True)
    deadline = models.DateField("Hạn khảo sát", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Khảo sát"
        verbose_name_plural = "Khảo sát"

    def __str__(self):
        return self.title


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    satisfaction_score = models.IntegerField("Điểm hài lòng (1-5)", null=True, blank=True)
    comments = models.TextField("Nhận xét", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phản hồi khảo sát"
        verbose_name_plural = "Phản hồi khảo sát"
        constraints = [
            models.UniqueConstraint(fields=["survey", "respondent"], name="uniq_survey_response_per_user"),
        ]

    def __str__(self):
        return f"Phản hồi #{self.pk}"

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Survey(models.Model):
    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    is_active = models.BooleanField('Đang mở', default=True)
    start_date = models.DateField('Bắt đầu', null=True, blank=True)
    end_date = models.DateField('Kết thúc', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Khảo sát'
        verbose_name_plural = 'Khảo sát'

    def __str__(self):
        return self.title


class SurveyQuestion(models.Model):
    QUESTION_TYPES = [('text','Văn bản'),('rating','Đánh giá 1-5'),('choice','Một lựa chọn'),('multi','Nhiều lựa chọn')]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField('Câu hỏi')
    question_type = models.CharField('Loại', max_length=10, choices=QUESTION_TYPES, default='text')
    options = models.JSONField('Lựa chọn', default=list, blank=True)
    is_required = models.BooleanField('Bắt buộc', default=False)
    order = models.IntegerField('Thứ tự', default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:80]


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    answers = models.JSONField('Câu trả lời', default=dict)
    overall_rating = models.IntegerField('Đánh giá tổng', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phản hồi khảo sát'

    def __str__(self):
        return f"Phản hồi khảo sát {self.survey.title}"

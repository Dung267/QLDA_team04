from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Survey(models.Model):
    title = models.CharField('Tiêu đề khảo sát', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    deadline = models.DateField('Hạn khảo sát', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Khảo sát'
        verbose_name_plural = 'Khảo sát'
    def __str__(self): return self.title

class SurveyQuestion(models.Model):
    TYPE_CHOICES = [('rating','Đánh giá 1-5'),('text','Văn bản'),('choice','Lựa chọn')]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField('Câu hỏi', max_length=300)
    question_type = models.CharField('Loại', max_length=10, choices=TYPE_CHOICES, default='rating')
    is_required = models.BooleanField('Bắt buộc', default=True)
    order = models.IntegerField('Thứ tự', default=0)
    class Meta:
        ordering = ['order']
    def __str__(self): return self.question_text

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    maintenance_request = models.ForeignKey('maintenance.MaintenanceRequest', on_delete=models.SET_NULL, null=True, blank=True)
    satisfaction_score = models.IntegerField('Điểm hài lòng (1-5)', null=True, blank=True)
    comments = models.TextField('Nhận xét', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Phản hồi khảo sát'
        verbose_name_plural = 'Phản hồi khảo sát'
    def __str__(self): return f"Phản hồi #{self.pk}"

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class DocumentCategory(models.Model):
    name = models.CharField('Danh mục', max_length=100)
    code = models.CharField('Mã', max_length=20, unique=True)
    class Meta:
        verbose_name = 'Danh mục tài liệu'
    def __str__(self): return self.name

class Document(models.Model):
    title = models.CharField('Tiêu đề', max_length=300)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, related_name='documents')
    description = models.TextField('Mô tả', blank=True)
    file = models.FileField('Tệp', upload_to='documents/')
    version = models.CharField('Phiên bản', max_length=20, default='1.0')
    infrastructure = models.ForeignKey('infrastructure.Infrastructure', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    road = models.ForeignKey('infrastructure.Road', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    is_public = models.BooleanField('Công khai', default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-created_at']
    def __str__(self): return self.title

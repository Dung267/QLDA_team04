from django.db import models


class MapLayer(models.Model):
    LAYER_TYPES = [('roads','Đường'),('lights','Đèn GT'),('flood','Ngập lụt'),('infra','Hạ tầng'),('weather','Thời tiết')]
    name = models.CharField(max_length=100)
    layer_type = models.CharField(max_length=10, choices=LAYER_TYPES)
    is_visible = models.BooleanField(default=True)
    style_config = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Lớp bản đồ'

    def __str__(self):
        return self.name

from rest_framework import serializers
from .models import ReportTemplate


class ReportTemplateSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_report_type_display', read_only=True)

    class Meta:
        model = ReportTemplate
        fields = '__all__'

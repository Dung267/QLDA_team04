from rest_framework import serializers
from .models import Survey, SurveyResponse


class SurveySerializer(serializers.ModelSerializer):
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = '__all__'

    def get_response_count(self, obj):
        return obj.responses.count()


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = '__all__'
        read_only_fields = ['respondent']

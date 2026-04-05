from rest_framework import serializers
from .models import Survey, SurveyQuestion, SurveyResponse


class SurveyQuestionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_question_type_display', read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = '__all__'


class SurveySerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, read_only=True)
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

from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.SurveyListAPIView.as_view(), name='api_survey_list'),
    path('<int:pk>/', api_views.SurveyDetailAPIView.as_view(), name='api_survey_detail'),
    path('<int:pk>/stats/', api_views.survey_stats_api, name='api_survey_stats'),
    path('responses/', api_views.SurveyResponseCreateAPIView.as_view(), name='api_survey_response'),
]

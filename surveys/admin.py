from django.contrib import admin
from .models import Survey, SurveyResponse

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "deadline", "created_by", "created_at"]
    list_filter = ["is_active", "deadline", "created_at"]
    search_fields = ["title", "description"]

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["survey", "respondent", "satisfaction_score", "created_at"]
    list_filter = ["survey", "created_at", "satisfaction_score"]
    search_fields = ["survey__title", "comments", "respondent__username"]

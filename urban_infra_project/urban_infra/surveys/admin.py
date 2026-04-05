from django.contrib import admin
from .models import Survey, SurveyQuestion, SurveyResponse

class QuestionInline(admin.TabularInline):
    model = SurveyQuestion
    extra = 2

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title','is_active','deadline','created_at']
    inlines = [QuestionInline]

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey','respondent','satisfaction_score','created_at']

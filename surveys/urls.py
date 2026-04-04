from django.urls import path
from . import views
app_name = 'surveys'
urlpatterns = [
    path('', views.survey_list, name='list'),
    path('<int:pk>/respond/', views.survey_respond, name='respond'),
]

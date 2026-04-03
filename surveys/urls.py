from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.survey_list, name='list'),
    path('<int:pk>/', views.survey_detail, name='detail'),
    path('<int:pk>/results/', views.survey_results, name='results'),
]

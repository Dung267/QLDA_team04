from django.urls import path
from . import views
app_name = 'surveys'
urlpatterns = [
    path('', views.SurveyListView.as_view(), name='list'),
    path('create/', views.SurveyCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SurveyDetailRespondView.as_view(), name='detail'),
    path('<int:pk>/respond/', views.SurveyDetailRespondView.as_view(), name='respond'),
    path('<int:pk>/results/', views.SurveyDetailRespondView.as_view(), name='results'),
]

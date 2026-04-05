from django.urls import path
from . import views
app_name = 'maps'
urlpatterns = [
    path('', views.map_view, name='map'),
    path('api/data/', views.map_data_api, name='data_api'),
]

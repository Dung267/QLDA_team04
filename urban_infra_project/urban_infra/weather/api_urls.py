from django.urls import path
from . import api_views

urlpatterns = [
    path('current/', api_views.current_weather_api, name='api_weather_current'),
    path('data/', api_views.WeatherDataListAPIView.as_view(), name='api_weather_data'),
    path('forecast/', api_views.WeatherForecastListAPIView.as_view(), name='api_weather_forecast'),
]

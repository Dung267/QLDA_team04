from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.api_urls')),
    path('infrastructure/', include('infrastructure.api_urls')),
    path('maintenance/', include('maintenance.api_urls')),
    path('flood/', include('flood.api_urls')),
    path('weather/', include('weather.api_urls')),
    path('chatbot/', include('chatbot.api_urls')),
]

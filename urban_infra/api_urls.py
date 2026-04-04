from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.api_urls')),
    path('infrastructure/', include('infrastructure.api_urls')),
    path('maintenance/', include('maintenance.api_urls')),
    path('notifications/', include('notifications.api_urls')),
    path('inventory/', include('inventory.api_urls')),
    path('flood/', include('flood.api_urls')),
    path('chatbot/', include('chatbot.api_urls')),
    path('hr/', include('hr.api_urls')),
    path('maps/', include('maps.api_urls')),
    path('contracts/', include('contracts.api_urls')),
    path('weather/', include('weather.api_urls')),
    path('surveys/', include('surveys.api_urls')),
    path('documents/', include('documents.api_urls')),
    path('backup/', include('backup.api_urls')),
    path('permits/', include('permits.api_urls')),
    path('vehicle-inspection/', include('vehicle_inspection.api_urls')),
    path('feedback/', include('feedback.api_urls')),
    path('integration/', include('integration.api_urls')),
    path('reports/', include('reports.api_urls')),
]

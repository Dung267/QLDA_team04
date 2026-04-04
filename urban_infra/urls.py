from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_header = 'Quản trị Hệ thống Hạ tầng Đô thị'
admin.site.site_title = 'Urban Infra Admin'
admin.site.index_title = 'Bảng điều khiển quản trị'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('urban_infra.core_urls')),
    path('accounts/', include('accounts.urls')),
    path('infrastructure/', include('infrastructure.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('notifications/', include('notifications.urls')),
    path('inventory/', include('inventory.urls')),
    path('flood/', include('flood.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('hr/', include('hr.urls')),
    path('maps/', include('maps.urls')),
    path('contracts/', include('contracts.urls')),
    path('weather/', include('weather.urls')),
    path('surveys/', include('surveys.urls')),
    path('documents/', include('documents.urls')),
    path('backup/', include('backup.urls')),
    path('permits/', include('permits.urls')),
    path('vehicle-inspection/', include('vehicle_inspection.urls')),
    path('feedback/', include('feedback.urls')),
    path('integration/', include('integration.urls')),
    path('reports/', include('reports.urls')),
    path('api/', include('urban_infra.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from .models import Area, Road, Pothole, TrafficLight

admin.site.register(Area)
admin.site.register(Road)
admin.site.register(Pothole)
admin.site.register(TrafficLight)
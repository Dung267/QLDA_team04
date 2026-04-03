from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def map_view(request):
    return render(request, 'maps/map.html', {'page_title': 'Bản đồ hạ tầng'})


def map_data_api(request):
    from infrastructure.models import Road, TrafficLight, Infrastructure
    data = {
        'roads': list(Road.objects.filter(latitude__isnull=False).values('id','name','status','latitude','longitude')),
        'lights': list(TrafficLight.objects.filter(latitude__isnull=False).values('id','code','status','latitude','longitude')),
        'infrastructure': list(Infrastructure.objects.filter(latitude__isnull=False).values('id','name','status','latitude','longitude')),
    }
    return JsonResponse(data)

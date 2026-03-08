# common/views.py

from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Urban Infrastructure Management System!")
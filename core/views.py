from django.shortcuts import render

from .models import User
from temperature.models import TemperatureController

def home(request):
    users = User.objects.all()
    controllers = [c.get_child() for c in TemperatureController.objects.all()]
    # [c.update() for c in controllers]
    return render(request, "main.html", {'users': users, 'controllers': controllers})

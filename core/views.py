from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import User
from temperature.models import TemperatureController


@login_required
def home(request):
    users = User.objects.all()
    controllers = [c.get_child() for c in TemperatureController.objects.all()]
    # [c.update() for c in controllers]
    return render(request, "main.html", {'users': users, 'controllers': controllers})

import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt


from .models import User, Device, Home
from temperature.models import TemperatureController
from power.models import Switch


@login_required
def main(request):
    users = User.objects.all()
    controllers = [c.get_child() for c in TemperatureController.objects.all()]
    devices = Device.objects.all()
    home = Home.objects.get()

    subs = {
        'user': request.user,
        'users': users,
        'controllers': controllers,
        'devices': devices,
        'switches': [s.get_child() for s in Switch.objects.all()],
        'home': home,
    }

    return render(request, "main.html", subs)


@csrf_exempt
def api_presence(request, user_id):
    user = User.objects.get(id=user_id)

    if user.api_key != request.POST.get('api_key'):
        raise PermissionDenied('invalid api key')

    device = Device.objects.get(id=request.POST['device_id'])
    device.is_present = json.loads(request.POST['state'])
    if device.is_present:
        device.last_seen = now()
    device.save()

    response_data = {
        'is_present': device.is_present
    }

    return JsonResponse(response_data)

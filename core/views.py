import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt


from .models import User, Device
from temperature.models import TemperatureController


@login_required
def main(request):
    users = User.objects.all()
    controllers = [c.get_child() for c in TemperatureController.objects.all()]
    # [c.update() for c in controllers]
    return render(request, "main.html", {'users': users, 'controllers': controllers})


@csrf_exempt
def api_presence(request, user_id):
    user = User.objects.get(id=user_id)

    data = json.loads(request.body)

    if user.api_key != data.get('api_key'):
        raise PermissionDenied('invalid api key')

    device = Device.objects.get(id=data['device_id'])
    device.is_present = data['is_present']
    device.last_seen = now()
    device.save()

    response_data = {
        'is_present': device.is_present
    }

    return JsonResponse(response_data)

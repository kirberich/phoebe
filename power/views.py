import json

from django.core.exceptions import PermissionDenied
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import User
from .models import Switch


@csrf_exempt
def toggle_switch(request, user_id, switch_id):
    user = User.objects.get(id=user_id)
    if user.api_key != request.POST.get('api_key'):
        raise PermissionDenied('invalid api key')
    switch = Switch.objects.get(id=switch_id).get_child()

    new_state = json.loads(request.POST['state'])
    if new_state:
        switch.on()
    else:
        switch.off()

    return JsonResponse({'is_on': new_state})

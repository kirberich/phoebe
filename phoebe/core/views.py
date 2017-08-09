import copy
import json

from channels import Group

from django.core.exceptions import PermissionDenied
from django.http.response import (
    HttpResponse,
    JsonResponse,
)
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from core.models import (
    Device,
    User,
)


LOOKUP_PRIORITY = [
    'id',
    'groups',
    'name__iexact',
    'groups__name__iexact',
    'friendly_name__iexact',
    'groups__friendly_name__iexact',
    'zone__name__iexact',
    'zone__friendly_name__exact',
]


def expand_command(user, command):
    """Expand a single human-friendly API command into device-level commands.

    A single request for an update of a group will turn into one command message for each device.
    """
    for lookup in LOOKUP_PRIORITY:
        try:
            devices = Device.objects.filter(zone__user=user, **{lookup: command['target']})
        except ValueError:
            # Ids are a special case because they're ints, just ignore the potential error for now.
            continue

        if devices:
            break

    expanded_commands = []
    for device in devices:
        message = {
            'command': command['command'],
            'device_type': device.device_type,
            'name': device.name,
            'data': copy.deepcopy(command['data'])
        }
        expanded_commands.append((device, message))

    return expanded_commands


@require_http_methods(['POST'])
@csrf_exempt
def command(request):
    """API endpoint for sending one or multiple commands to various targets.

    Accepts either a single command or a list of commands.

    Commands all follow this structure
    {
        'command': <command>,
        'target': device identifier (see LOOKUP_PRIORITY for options)
        'data': <command_specific_data>
    }

    Commands get expanded into per-device messages and then normalized -
    only one command is ever executed per device and command type
    """

    # Get the token
    token = request.GET.get('token')
    if not token:
        raise PermissionDenied("Token required!")

    try:
        user = User.objects.get(api_key=token)
    except User.DoesNotExist:
        raise PermissionDenied("Invalid token!")

    try:
        data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return HttpResponse("Invalid json!", status=400)

    # Allow sending just a single command as well as a list, to keep things nice and simple.
    if isinstance(data, dict):
        data = [data]

    # Go through commands in order and store them by command and device id -
    # when multiple commands of the same type are required for one device, later commands override old ones.
    # Commands are not just overwritten, but combined.
    grouped_commands = {}
    for command in data:
        expanded_commands = expand_command(user, command)
        for device, message in expanded_commands:
            command_key = '{}-{}'.format(device.id, message['command'])

            if command_key not in grouped_commands:
                grouped_commands[command_key] = (device, message)
            else:
                grouped_commands[command_key][1]['data'].update(message['data'])

    sent_messages = []
    for device, message in grouped_commands.values():
        group = Group("user_{}_zone_{}".format(device.zone.user_id, device.zone.name))
        group.send({'text': json.dumps(message)})
        sent_messages.append(message)

    return JsonResponse({'sent_messages': sent_messages})

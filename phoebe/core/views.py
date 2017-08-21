from collections import defaultdict
import copy
import json
from random import randint

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
    Zone,
)
from core.signals import event


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


def handle_device_command(user, command):
    """Expand a single human-friendly API command into device-level commands.

    A single request for an update of a group will turn into one command message for each device.
    """
    target = command.get('target')
    if not target:
        return {'errors': ['No target supplied in command data!']}

    for lookup in LOOKUP_PRIORITY:
        try:
            devices = Device.objects.filter(zone__user=user, **{lookup: command['target']})
        except ValueError:
            # Ids are a special case because they're ints, just ignore the potential error for now.
            continue

        if devices:
            break

    messages = []
    for device in devices:
        message = {
            'command': command['command'],
            'device_type': device.device_type,
            'name': device.name,
            'data': copy.deepcopy(command['data'])
        }
        messages.append((device, message))

    return {'messages': messages, 'data': '{} commands sent'.format(len(messages))}


def handle_event_command(user, command):
    zone_name = command.get('zone')
    if not zone_name:
        return {'errors': ['No zone supplied in command data!']}

    zone = Zone.objects.filter(user=user, name=zone_name).first()
    if not zone:
        return {'errors': ['Zone with name {} does not exist for this user!'.format(zone_name)]}

    event_type = command.get('target')
    if not event_type:
        return {'errors': ['No event supplied in command data!']}

    event.send(
        sender='command',
        event_type=event_type,
        zone=zone,
        user=user,
        data=command.get('data')
    )

    return {'data': "success"}


@require_http_methods(['POST'])
@csrf_exempt
def command(request):
    """API endpoint for executing one or multiple commands.

    Commands all follow this structure
    {
        'command': <command>,
        'target': device identifier (where applicable) (see LOOKUP_PRIORITY for options)
        'data': <command_specific_data>
    }

    Targeted commands get expanded into per-device messages and then normalized -
    only one command is ever executed per event and command type.

    Global commands aren't normalized and will all be executed as requested.
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

    response = defaultdict(dict)
    messages = {}
    for command in data:
        handler = COMMAND_HANDLERS.get(command['command'])
        target = command.get('target')
        command_id = command.get('id', "{}-{}".format(
            command['command'],
            target or randint(0, 100000)
        ))
        if not handler:
            response['errors'][command_id] = "Unknown command '{}'".format(command['command'])

        result = handler(user, command) or {}

        if 'errors' in result:
            response['errors'][command_id] = result['errors']

        if 'data' in result:
            response['data'][command_id] = result['data']

        if 'messages' in result:
            for device, message in result['messages']:
                # Messages as returned by commands are always in the format of
                # (device, message), with message having the standard format of
                # {
                #     "command": command,
                #     "data": data,
                #     "name": device name,
                #     "device_type": device type
                # }
                command_key = '{}-{}'.format(device.id, message['command'])

                if command_key not in messages:
                    messages[command_key] = (device, message)
                else:
                    messages[command_key][1]['data'].update(message['data'])

    # Go through the grouped messages and send them out
    for device, message in messages.values():
        group = Group("user_{}_zone_{}".format(device.zone.user_id, device.zone.name))
        group.send({'text': json.dumps(message)})

    return JsonResponse(response)


COMMAND_HANDLERS = {
    'set_state': handle_device_command,
    'trigger_event': handle_event_command
}

from functools import wraps
import json

from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.db import transaction
from channels import Group

from core.models import (
    Device,
    DeviceGroup,
    Zone,
)
from django.utils import timezone


class CommandError(Exception):
    """Top-level exception for client errors in commands."""


def handle_replies(f):
    """Decorator for commands to make it easy to return responses to the sending websocket."""
    @wraps(f)
    def wrapper(message):
        user_id = message.channel_session.get('user_id')
        message.user = get_user_model().objects.get(id=user_id) if user_id else None

        try:
            response_data = f(message)
        except CommandError as e:
            message.reply_channel.send({
                'text': json.dumps({
                    'command': 'error',
                    'error_message': str(e)
                })
            })
        else:
            if isinstance(response_data, str):
                response_data = {'command': 'success', 'data': response_data}
            if response_data:
                if isinstance(response_data, list):
                    for message_data in response_data:
                        message.reply_channel.send({
                            'text': json.dumps(message_data)
                        })
                else:
                    message.reply_channel.send({
                        'text': json.dumps(response_data)
                    })

    return wrapper


@transaction.atomic
def handle_login(message, data):
    if not data.get('username') or not data.get('password'):
        raise CommandError("Login requires username and password")

    user = authenticate(username=data['username'], password=data['password'])
    zone_name = data['zone']
    if user:
        message.channel_session['user_id'] = user.pk
        message.user = user

        # On logging in, make sure the bridge's zone exists (can't be done before login)
        Zone.objects.get_or_create(
            name=zone_name,
            user=user
        )
        message.channel_session['zone_name'] = zone_name

        # Now, record add the socket to the appropriate groups
        Group("user_{}".format(user.id)).add(message.reply_channel)
        Group("user_{}_zone_{}".format(user.id, zone_name)).add(message.reply_channel)

        return {'command': 'login_success'}
    else:
        raise CommandError("Invalid user or password")


def handle_logout(message, data):
    message.channel_session['user_id'] = None
    message.user = None
    return 'Successfully logged out.'


def handle_update_group(message, data):
    command_data = data['data']
    if not command_data.get('name'):
        raise CommandError("update_group requires a device name!")

    DeviceGroup.objects.update_or_create(
        name=command_data['name'],
        zone=Zone.objects.get(name=message.channel_session['zone_name']),
        defaults={
            'friendly_name': command_data['friendly_name']
        }
    )


def handle_update_device(message, data):
    """ Update the state of a device """
    # Validate command
    command_data = data['data']
    if not command_data.get('name'):
        raise CommandError("update_device requires a device name!")

    zone = Zone.objects.get(name=message.channel_session['zone_name']),
    group_name = command_data.pop('device_group', '')

    try:
        device = Device.objects.get(
            name=command_data['name'],
            device_type=command_data['device_type']
        )

        if command_data.get('data'):
            device.data = command_data['data']
            device.last_seen = timezone.now()
            device.last_updated = timezone.now()
            device.zone = zone
            device.save(data_source='device')

    except Device.DoesNotExist:
        # To allow creating the device, we need to double-check that the device group exists
        device = Device(
            zone=zone,
            **command_data
        )
        device.save(data_source='device')

    if group_name:
        device_group, created = DeviceGroup.objects.get_or_create(
            name=group_name
        )

        if device_group not in device.groups.all():
            device.groups.add(device_group)


def handle_get_devices(message, data):
    command_data = data['data']

    filters = {}
    if 'name' in command_data:
        filters['name'] = command_data['name']
    if 'group' in command_data:
        filters['device_group__name'] = command_data['group']
    if 'type' in command_data:
        filters['device_type'] = command_data['type']

    devices = Device.objects.filter(**filters)

    response_data = [{
        'command': 'set_state',
        'device_type': device.device_type,
        'name': device.name,
        'data': device.data
    } for device in devices]
    return response_data


available_commands = {
    'login': handle_login,
    'logout': handle_logout,
    'echo': lambda message, data: message['text'],
    'whoami': lambda message, data: {'command': 'whoami', 'username': str(message.user or 'anonymous')},
    'update_device': handle_update_device,
    'update_group': handle_update_group,
    'get_devices': handle_get_devices,
}


@handle_replies
def handle_command(message):
    """Main entry point for all commands coming in via websocket."""
    try:
        data = json.loads(message['text'])
    except json.decoder.JSONDecodeError as e:
        raise CommandError("Invalid json.{}".format(e))

    if 'command' not in data:
        raise CommandError("No command given")

    if data['command'] != 'login' and not message.channel_session['user_id']:
        raise Exception("Login required")

    command_handler = available_commands.get(data['command'])

    if not command_handler:
        raise CommandError("Unknown command {}".format(data['command']))
    return command_handler(message, data)

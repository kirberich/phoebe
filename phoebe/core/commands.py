from functools import wraps
import json

from django.contrib.auth import (
    authenticate, 
    get_user_model,
    SESSION_KEY
)

from core.models import Device
from django.utils import timezone


class CommandError(Exception):
    pass


def handle_replies(f):
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
                    'error_message': e.msg
                })
            })
        else:
            if isinstance(response_data, str):
                response_data = {'command': 'success', 'data': response_data}
            message.reply_channel.send({
                'text': json.dumps(response_data)
            })

    return wrapper


def handle_login(message, data):
    if not data.get('username') or not data.get('password'):
        raise CommandError("Login requires username and password")

    user = authenticate(username=data['username'], password=data['password'])
    if user:
        message.channel_session['user_id'] = user.pk
        message.user = user
        return 'Successfully logged in as {}'.format(user)
    else:
        raise CommandError("Invalid user or password")


def handle_logout(message, data): 
    message.channel_session['user_id'] = None
    message.user = None
    return 'Successfully logged out.'


def handle_update_device(message, data):
    """ Update the state of a device """
    # Validate command
    if not data.get('id'):
        raise CommandError("update_device requires an id!")

    try:
        device = Device.objects.get(pk=data['id'])
    except Device.DoesNotExist:
        raise CommandError("Device {} does not exist.".format(data['id']))

    if data.get('data'):
        device.data = data['data']
        device.last_seen = timezone.now()
        device.last_updated = timezone.now()
        device.save()


available_commands = {
    'login': handle_login,
    'logout': handle_logout,
    'echo': lambda message, data: message['text'],
    'whoami': lambda message, data: {'command': 'whoami', 'username': str(message.user or 'anonymous')},
    'update_device': handle_update_device,
}


@handle_replies
def handle_command(message):
    try:
        data = json.loads(message['text'])
    except json.decoder.JSONDecodeError as e:
        raise CommandError("Invalid json.{}".format(e))

    if not 'command' in data:
        raise CommandError("No command given")

    command_handler = available_commands.get(data['command'])
    if not command_handler:
        raise CommandError("Unknown command {}".format(data['command']))
    return command_handler(message, data)

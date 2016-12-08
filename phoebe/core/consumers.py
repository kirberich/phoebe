from channels import Group
from channels.sessions import channel_session

from core.models import DeviceGroup
from core.commands import handle_command


@channel_session
def ws_connect(message):
    zone_name = message['path'].strip("/").split("/")[0]
    message.channel_session['zone_name'] = zone_name


@channel_session
def ws_receive(message):
    handle_command(message)


@channel_session
def ws_disconnect(message):
    user_id = message.channel_session.get('user_id')
    zone_name = message.channel_session.get('zone_name')

    if user_id:
        Group("user_{}".format(user_id)).discard(message.reply_channel)
    if user_id and zone_name:
        Group("user_{}_zone_{}".format(user_id, zone_name)).discard(message.reply_channel)

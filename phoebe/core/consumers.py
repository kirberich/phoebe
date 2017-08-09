import json

from channels import Group
from channels.sessions import channel_session

from core.commands import handle_command


@channel_session
def ws_connect(message):
    message.channel_session['user_id'] = None  # Do JWT things here


@channel_session
def ws_receive(message):
    return handle_command(message)


@channel_session
def ws_disconnect(message):
    user_id = message.channel_session.get('user_id')

    if user_id:
        Group("user_{}".format(user_id)).discard(message.reply_channel)

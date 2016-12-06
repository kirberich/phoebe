from channels import Group
from channels.sessions import channel_session

from core.models import DeviceGroup
from core.commands import handle_command


def ws_connect(message):
    pass


@channel_session
def ws_receive(message):
    handle_command(message)


def ws_disconnect(message):
    pass

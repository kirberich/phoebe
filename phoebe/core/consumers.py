from channels import Group


def ws_connect(message, zone):
    Group(zone).add(message.reply_channel)
    message.reply_channel.send({
        "text": 'connected to {}'.format(message['path']),
    })

def ws_receive(message, zone):
    """ echo websocket test """
    zone_group = Group(zone)
    zone_group.send({
        "text": zone,
    })

def ws_disconnect(message, zone):
    Group("chat").discard(message.reply_channel)
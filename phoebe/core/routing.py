from channels import route

from core import consumers

websocket_routing = [
    route("websocket.connect", consumers.ws_connect),
    route("websocket.receive", consumers.ws_receive),
    route("websocket.disconnect", consumers.ws_disconnect),
]

from channels import route

from core import consumers


websocket_routing = [
    route("websocket.connect", consumers.ws_connect, path=r'^/(?P<zone>[^/]+)/$'),
    route("websocket.receive", consumers.ws_receive, path=r'^/(?P<zone>[^/]+)/$'),
    route("websocket.disconnect", consumers.ws_disconnect, path=r'^(?P<zone>[^/]+)/$'),
]
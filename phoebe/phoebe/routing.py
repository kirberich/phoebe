from channels import include

channel_routing = [
    include("core.routing.websocket_routing", path=r"^/ws"),
]
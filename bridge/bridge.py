import time
import json
import tornado

from websocket import (
    Client,
    make_server
)
import settings


class Bridge():
    commands = {
        'set_device': 'forward_message',
        'success': 'print_message'
    }

    def __init__(self, server_url, local_port=8888):
        self.server_url = server_url
        self.local_port = local_port
        self.clients = set([])

        self.client = Client(
            self.server_url,
            message_handler=self.client_callback,
            connect_handler=self.connect_callback
        )
        self.main_io_loop = tornado.ioloop.IOLoop.instance()
        self.periodic_callback = tornado.ioloop.PeriodicCallback(
            self.periodic_callback, 
            1000, 
            io_loop=self.main_io_loop
        )

        self.server_tornado_application = tornado.web.Application([
            (r'/', make_server(
                connect_handler=self.new_client_callback,
                message_handler=self.server_callback,
                disconnect_handler=self.client_disconnected_callback
            )),
        ])
        self.server = tornado.httpserver.HTTPServer(self.server_tornado_application)

    def start(self):
        self.client.connect()
        self.periodic_callback.start()
        self.server.listen(self.local_port)

        try:
            self.main_io_loop.start()
        except KeyboardInterrupt:
            self.client.close()

    def connect_callback(self):
        print("connection established")

        # Authenticate with phoebe
        time.sleep(1)
        self.client.send({
            'command': 'login',
            'username': settings.username,
            'password': settings.password
        })

    def periodic_callback(self):
        print("periodic callback")
        print(self.clients)

    def print_message(self, message):
        print(message)

    def forward_message(self, message):
        for client in self.clients:
            client.write_message(message)

    def client_callback(self, message):
        print("received data from phoebe server: {}".format(message))
        decoded = json.loads(message)

        if 'command' not in message:
            return

        command = getattr(self, self.commands.get(decoded['command'], 'print_message'))
        return command(message)

    def new_client_callback(self, server):
        self.clients.add(server)

    def server_callback(self, message):
        """ Messages received from local devices to be forwarded to phoebe. """
        print("received data from local device: {}".format(message))
        self.client.send(message)

    def client_disconnected_callback(self, server):
        self.clients.remove(server)


if __name__ == '__main__':
    full_url = settings.phoebe_server + settings.zone
    bridge = Bridge(full_url)
    bridge.start()

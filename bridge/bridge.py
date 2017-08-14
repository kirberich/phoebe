import time
import json
from os.path import (
    join,
    dirname,
    exists,
)
from urllib.parse import urljoin

import tornado


from websocket import (
    Client,
    make_server
)


CONFIG_FILE = join(dirname(__file__), 'settings.json')
CONFIG_DEFAULTS = {
    'phoebe_url': 'ws://localhost:8000/',
    'bridge_url': 'ws://localhost:8888/',
    'zone': 'home',
    'username': '',
    'password': ''
}


class Bridge:
    """Central bridge for all devices. This gathers and broadcasts to and from the cloud service."""

    def __init__(self, local_port=8888):
        self.config = self.load_configuration()
        self.server_url = urljoin(self.config['phoebe_url'], self.config['zone'])
        self.local_port = local_port
        self.clients = set([])
        self.is_logged_in = False

        self.client = Client(
            self.server_url,
            message_handler=self.client_callback,
            connect_handler=self.connect_callback
        )
        self.main_io_loop = tornado.ioloop.IOLoop.instance()
        self.periodic_callback = tornado.ioloop.PeriodicCallback(
            self.periodic_callback_handler,
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

    def load_configuration(self):
        if not exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'phoebe': CONFIG_DEFAULTS}, f, indent=4)
                return CONFIG_DEFAULTS

        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)['phoebe']

    def start(self):
        self.client.connect()
        self.periodic_callback.start()
        self.server.listen(self.local_port)

        try:
            self.main_io_loop.start()
        except KeyboardInterrupt:
            self.client.close()

    def login(self):
        # Authenticate with phoebe
        print("Attempting login...")
        self.client.send({
            'command': 'login',
            'username': self.config['username'],
            'password': self.config['password']
        })

    def connect_callback(self):
        print("connection established")
        time.sleep(1)
        self.login()

    def periodic_callback_handler(self):
        # Retry login if it hasn't worked so far
        if not self.is_logged_in:
            self.login()

    def client_callback(self, message):
        print("received data from phoebe server: {}".format(message))
        decoded = json.loads(message)

        if 'command' not in message:
            return

        command = self.commands.get(decoded['command'])
        if command:
            return command(self, message)
        else:
            self.forward_message(message)

    def new_client_callback(self, server):
        print("new client")
        self.clients.add(server)

    def server_callback(self, message):
        """ Messages received from local devices to be forwarded to phoebe. """
        print("received data from local device: {}".format(message))
        self.client.send(message)

    def client_disconnected_callback(self, server):
        self.clients.remove(server)

    # Command handlers

    def forward_message(self, message):
        for client in self.clients:
            client.write_message(message)

    def login_success_handler(self, message):
        self.is_logged_in = True

    def print_message(self, message):
        print(message)

    commands = {
        'set_state': forward_message,
        'device_state': forward_message,
        'login_success': login_success_handler,
        'success': print_message
    }


if __name__ == '__main__':
    bridge = Bridge()
    bridge.start()

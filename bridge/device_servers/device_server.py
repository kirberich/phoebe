"""Base for all servers that update local devices and report to the bridge."""

import logging
from os.path import (
    join,
    dirname,
)
import json

import tornado

from websocket import Client


CONFIG_FILE = join(dirname(dirname(__file__)), 'settings.json')


class DeviceServer:
    """Base class for all bridge device servers."""

    # Set this key in subclasses to define where server configuration is stored
    configuration_key = None
    device_filter = None

    def __new__(cls):
        self = super().__new__(cls)

        if not self.configuration_key:
            raise Exception("configuration_key needs to be set in {}".format(type(self)))

        if not self.device_filter:
            raise Exception("device_filter needs to be set in {}".format(type(self)))

        self.config = self.load_configuration(self.configuration_key)

        phoebe_config = self.load_configuration('phoebe')
        self.client = Client(
            phoebe_config['bridge_url'],
            connect_handler=self.connect_callback,
            message_handler=self.message_callback,
        )
        self.main_io_loop = tornado.ioloop.IOLoop.instance()

        return self

    def start(self):
        self.on_start()
        self.client.connect()

        try:
            self.main_io_loop.start()
        except KeyboardInterrupt:
            self.client.close()

    def load_configuration(self, key):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f).get(key, {})

    def save_configuration(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        config[self.configuration_key] = self.config

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def connect_callback(self):
        pass

    def on_start(self):
        pass

    def message_callback(self, message):
        """Handle incoming device commands."""
        message_data = json.loads(message)

        if 'device_type' not in message_data or not message_data['device_type'].startswith(self.device_filter):
            return

        # Try to find a matching command and execute it
        command_name = message_data['command']
        command_data = message_data['data']
        device_name = message_data['name']

        command_handler_name = 'command_{}'.format(command_name)
        if not hasattr(self, command_handler_name):
            logging.info("{} does not support command {}".format(
                self,
                command_name
            ))

        command_handler = getattr(self, command_handler_name)
        return command_handler(device_name, command_data)

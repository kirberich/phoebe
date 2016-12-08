import json
import os
import sys
import time

import tornado

from huegely import Bridge
from huegely.exceptions import HueError

from websocket import Client
from device import Device


class HueServer():
    def __init__(self, phoebe_bridge_url='ws://localhost:8888/'):
        self.phoebe_bridge_url = phoebe_bridge_url

        if not os.path.exists('hue_config.json'):
            raise Exception("Please run configuration first to set up hue lights.")

        with open('hue_config.json', 'r') as f:
            hue_config = json.load(f)

        self.hue_bridge = Bridge(hue_config['ip'], hue_config['username'])
        self.phoebe_bridge_port = 8888

        self.client = Client(
            self.phoebe_bridge_url,
            connect_handler=self.connect_callback,
            message_handler=self.message_callback,
        )
        self.main_io_loop = tornado.ioloop.IOLoop.instance()

        self.periodic_callback = tornado.ioloop.PeriodicCallback(
            self.update_devices, 
            10000, 
            io_loop=self.main_io_loop
        )

        self.devices = {}

    def start(self):
        self.client.connect()
        self.periodic_callback.start()

        try:
            self.main_io_loop.start()
        except KeyboardInterrupt:
            self.client.close()

    def update_devices(self):
        """ Send updates of any changed lights to phoebe. """
        rooms = [g for g in self.hue_bridge.groups() if g.group_type() == 'Room']

        for room in rooms:
            for light in room.lights():
                light_device = Device(
                    name=light.device_id,
                    device_group=room.device_id,
                    device_type="hue."+light.__class__.__name__,
                    friendly_name=light.name(),
                    data=light.state()
                )
                
                if light.device_id not in self.devices or self.devices[light.device_id] != light_device:
                    self.client.send({
                        'command': 'update_device', 
                        'data': light_device.to_dict()
                    })
                    self.devices[light.device_id] = light_device


    def connect_callback(self):
        rooms = [g for g in self.hue_bridge.groups() if g.group_type() == 'Room']
        for room in rooms:
            self.client.send({
                'command': 'update_group', 
                'data': {
                    'name': room.device_id,
                    'friendly_name': room.name()
                }
            })
            
        self.update_devices()

    def message_callback(self, message):
        print("hue server received message {}".format(message))
        decoded = json.loads(message)

        if 'device_type' not in decoded or not decoded['device_type'].startswith('hue.'):
            return

        light = [l for l in self.hue_bridge.lights() if l.device_id == int(decoded['name'])][0]

        data = decoded['data']
        light.state(
            brightness=data['brightness'],
            hue=data['hue'],
            saturation=data['saturation'],
            on=data['on']
        )


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--configure':
        hue_ip = input("Please enter the ip address of your hue bridge: ")
        bridge = Bridge(hue_ip)
        print("Please press the button on your hue bridge...")

        start_time = time.time()
        while time.time() - 60 < start_time:
            try:
                token = bridge.get_token('phoebe-hue')
                break
            except HueError:
                time.sleep(1)
                print(".", end='')
                sys.stdout.flush()

        with open('hue_config.json', 'w') as f:
            f.write(json.dumps({'ip': hue_ip, 'username': token}))
        print("Thanks, you can now start the server normally.")
        exit(0)

    hue_server = HueServer()
    hue_server.start()
"""Server for watching and updating hue devices."""
import logging
import sys
import time
from datetime import (
    datetime,
    timedelta,
)

from tornado import (
    gen,
    locks,
)

from huegely import Bridge
from huegely.exceptions import HueError

from device import Device

from .device_server import DeviceServer


UPDATE_INTERVAL = 1
ROOM_UPDATE_INTERVAL = 30

lock = locks.Lock()


class HueServer(DeviceServer):
    """The Hue Server polls the hue bridge for updates and reports/handles updates to/from the central bridge."""

    configuration_key = 'hue'
    device_filter = 'hue.'

    def __init__(self):
        self.devices = {}
        self.rooms_last_updated = datetime.now()
        self.rooms = []

        if 'ip' not in self.config or 'username' not in self.config:
            self.configure()

        self.hue_bridge = Bridge(self.config['ip'], self.config['username'])

    def configure(self):
        self.config['ip'] = self.config.get('ip') or input("Please enter the ip address of your hue bridge: ")
        bridge = Bridge(self.config['ip'])

        if not self.config.get('username'):
            print("Please press the button on your hue bridge...")

            start_time = time.time()
            while time.time() - 60 < start_time:
                try:
                    self.config['username'] = bridge.get_token('phoebe-hue')
                    break
                except HueError:
                    time.sleep(1)
                    print(".", end='')
                    sys.stdout.flush()

        self.save_configuration()

    def on_start(self):
        self.update_devices()

    def _report_device_update(self, device):
        print("sending data....")
        self.client.send({
            'command': 'update_device',
            'data': device.to_dict()
        })

    def _update_devices(self):
        """Send updates of any changed lights to the bridge."""
        # Update rooms if necessary - rooms change very rarely, so there's no need updating them as frequently as lights
        if not self.rooms or datetime.now() > self.rooms_last_updated + timedelta(seconds=ROOM_UPDATE_INTERVAL):
            self.rooms_last_updated = datetime.now()
            self.rooms = [g for g in self.hue_bridge.groups() if g.group_type() == 'Room']
            print("scanned {} rooms".format(len(self.rooms)))

        for room in self.rooms:
            for light in room.lights():
                print("scanned light {}".format(light.device_id))

                light_device = Device(
                    name=light.device_id,
                    device_group=room.device_id,
                    device_type="hue." + light.__class__.__name__,
                    friendly_name=light._name,
                    data=light.state()
                )

                if light.device_id not in self.devices or self.devices[light.device_id] != light_device:
                    self.devices[light.device_id] = light_device

                    # Don't try to send anything if we're not connected to the bridge
                    if not self.client.is_connected:
                        continue

                    self._report_device_update(light_device)

    @gen.coroutine
    def update_devices(self):
        try:
            with (yield lock.acquire()):
                self._update_devices()
        except Exception:
            logging.exception("Something went wrong trying to update devices")
        finally:
            # Schedule the next device update. We're doing this instead of a periodic timeout to allow
            # taking into account the time it takes the scan to run.
            self.main_io_loop.call_later(
                UPDATE_INTERVAL,
                self.update_devices,
            )

    def connect_callback(self):
        """Send all known data on connect to make sure the bridge is fully updated."""
        if not self.rooms:
            raise Exception("Rooms not loaded yet, make sure to update devices before the connect callback runs!")

        for room in self.rooms:
            self.client.send({
                'command': 'update_group',
                'data': {
                    'name': room.device_id,
                    'friendly_name': room.name()
                }
            })

        for device_id, device in self.devices.items():
            self._report_device_update(device)

    def _set_state(self, device_name, data):
        light = [l for l in self.hue_bridge.lights() if l.device_id == int(device_name)][0]

        try:
            light.state(
                brightness=data.get('brightness'),
                hue=data.get('hue'),
                saturation=data.get('saturation'),
                on=data['on']
            )
        except HueError:
            logging.exception("Couldn't update hue device!")
            # Generally an error like this means we tried to send unsupported state.
            # In a case like that, we'll want to send back the real state.
            if light.device_id in self.devices:
                self._report_device_update(self.devices[light.device_id])

    @gen.coroutine
    def command_set_state(self, device_name, data):
        with (yield lock.acquire()):
            return self._handle_set_state(device_name, data)

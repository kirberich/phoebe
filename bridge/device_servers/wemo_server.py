import logging

from ouimeaux.device import switch

from device import Device
from .device_server import DeviceServer

UPDATE_INTERVAL = 1
WEMO_URL_PATTERN = "http://{}:49153/setup.xml"


class WeMoServer(DeviceServer):
    """Device server for WeMo devices (cheap wifi switches)."""

    configuration_key = 'wemo'
    device_filter = 'wemo.'

    def __init__(self):
        # WeMo devices are stored by ip address
        self.devices = {}

    def on_start(self):
        self.update_devices()

    def _report_device_update(self, device):
        self.client.send({
            'command': 'update_device',
            'data': device.to_dict()
        })

    def _update_devices(self):
        """Send updates of any changed devices to the bridge."""
        for ip, device in self.devices.items():
            wemo_switch = switch.Switch(WEMO_URL_PATTERN.format(ip))

            is_on = bool(wemo_switch.get_state())
            if device.data['on'] != is_on:
                device.data['on'] = is_on

                # Don't try to send anything if we're not connected to the bridge
                if not self.client.is_connected:
                    continue

                self._report_device_update(device)

    def update_devices(self):
        try:
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
        self.client.send({
            'command': 'get_devices',
            'data': {
                'type': 'wemo.switch'
            }
        })

    def register_device(self, name, data):
        if 'ip' not in data:
            print("Got data but no ip, not using this message to register a new device")
            return

        if data['ip'] in self.devices:
            device = self.devices[data['ip']]
        else:
            print("Registered new device {}".format(name))

            self.devices[data['ip']] = Device(
                device_type='wemo.switch',
                name=name,
                data=data
            )
        return device

    def command_set_state(self, device_name, data):
        self.register_device(device_name, data)

        for ip, device in self.devices.items():
            if device.name != device_name:
                continue

            self.devices[ip].data['on'] = data['on']
            wemo_switch = switch.Switch(WEMO_URL_PATTERN.format(ip))
            wemo_switch.set_state(data['on'])

    def command_get_state(self, device_name, data):
        device = self.register_device(device_name, data)
        if device:
            self._report_device_update(device)

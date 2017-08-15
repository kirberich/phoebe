import logging
from datetime import (
    datetime,
    timedelta,
)


from device import Device
from .device_server import DeviceServer

UPDATE_INTERVAL = 1
DEVICE_UPDATE_INTERVAL = 60


def get_switch_class():
    """The orvibo library opens a server socket on import.

    To make sure the library only gets imported in the single server that actually uses orvibo,
    we do the import here.
    """
    from orvibo.s20 import S20
    return S20


class OrviboServer(DeviceServer):
    """Device server for Orvibo devices (cheap wifi switches)."""

    configuration_key = 'orvibo'
    device_filter = 'orvibo.'

    def __init__(self):
        # Orvibo devices are stored by ip address
        self.devices = {}
        self.devices_last_updated = datetime.now()

    def _discover_devices(self):
        before = datetime.now()
        hosts = self.discover()

        self.devices = {}
        for ip, host_data in hosts.items():
            device = Device(
                name=ip,
                device_type="orvibo.s20",
                friendly_name='Orvibo Switch {}'.format(ip),
                data={
                    'on': bool(host_data['st']),
                    'ip': ip
                }
            )
            self.devices[ip] = device

        print("Discovered {} devices in {} seconds".format(len(self.devices), datetime.now() - before))

    def discover(self):
        from orvibo.s20 import discover
        return discover()

    def on_start(self):
        self._discover_devices()
        self.update_devices()

    def _report_device_update(self, device):
        self.client.send({
            'command': 'update_device',
            'data': device.to_dict()
        })

    def _update_devices(self):
        """Send updates of any changed devices to the bridge."""
        if datetime.now() > self.devices_last_updated + timedelta(seconds=DEVICE_UPDATE_INTERVAL):
            self.devices_last_updated = datetime.now()
            self._discover_devices()

        for ip, device in self.devices.items():
            orvibo_device = get_switch_class()(ip)

            is_on = bool(orvibo_device.on)
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
        for device in self.devices.values():
            self._report_device_update(device)

    def command_set_state(self, device_name, data):
        for ip, device in self.devices.items():
            if device.name != device_name:
                continue

            device.on = data['on']
            orvibo_device = get_switch_class()(ip)
            orvibo_device.on = data['on']

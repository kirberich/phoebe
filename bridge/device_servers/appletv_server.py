import logging
from datetime import datetime
import re
import subprocess

from device import Device
from .device_server import DeviceServer

UPDATE_INTERVAL = 1

SCAN_REGEX = " - (?P<device_name>\w+) at (?P<ip_address>[0-9\.]+) \(login id: (?P<login_id>[0-9a-z\-]+)\)"
CURRENTLY_PLAYING_REGEX = '(?P<key>[^\:]+)\: (?P<value>.+)'


class AppleTVServer(DeviceServer):
    """Device server for AppleTV."""

    configuration_key = 'appletv'
    device_filter = 'appletv'

    def __init__(self):
        # AppleTV devices are stored by ip address
        self.devices = {}
        self.devices_last_updated = datetime.now()

    def _execute_command(self, command, non_blocking=False):
        if isinstance(command, list):
            combined_command = ['atvremote'] + command
        else:
            combined_command = ['atvremote', command]

        if non_blocking:
            return subprocess.Popen(combined_command)

        output = subprocess.check_output(combined_command).decode('utf-8')
        rows = output.split("\n")
        return rows

    def currently_playing(self, device):
        command = ['--address', device.data['ip'], '--login_id', device.data['login_id'], 'playing']
        output = self._execute_command(command)

        data = {}
        for row in output:
            row = row.strip()
            m = re.search(CURRENTLY_PLAYING_REGEX, row)
            if m:
                groups = m.groupdict()
                data[groups['key']] = groups['value']

        return data

    def play_url(self, device, url):
        command = [
            '--address', device.data['ip'],
            '--login_id', device.data['login_id'],
            '--airplay_credentials', 'E45861DC4ADEEB80:71F0ACC8F96B1B8FA584F68B25E6F7260DEDF4973ACDD6BDEF3150AED4CA458C',
            'play_url={}'.format(url),
            '&'
        ]
        print(command)
        output = self._execute_command(command, non_blocking=True)
        print(output)

    def _discover_devices(self):
        output = self._execute_command('scan')
        self.devices = {}
        for row in output:
            m = re.search(SCAN_REGEX, row)
            if m:
                groups = m.groupdict()

                device = Device(
                    name=groups['device_name'],
                    device_type='appletv',
                    friendly_name=groups['device_name'],
                    data={
                        'ip': groups['ip_address'],
                        'login_id': groups['login_id'],
                    }
                )
                device.data['state'] = self.currently_playing(device)
                self.devices[groups['ip_address']] = device
        print("Found {} apple tvs!".format(len(self.devices)))

    def on_start(self):
        while not self.devices:
            self._discover_devices()

            if not self._discover_devices:
                print("No apple tv's found yet...")

        self.update_devices()

    def _report_device_update(self, device):
        self.client.send({
            'command': 'update_device',
            'data': device.to_dict()
        })

    def _update_devices(self):
        """Send updates of any changed devices to the bridge."""
        print("scanning...")
        for ip, device in self.devices.items():
            state = self.currently_playing(device)

            print(state)
            if device.data['state'] != state:
                device.data['state'] = state

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

    def command_play_url(self, device_name, data):
        for device in self.devices.values():
            if device.name != device_name:
                continue
            self.play_url(device, data['url'])

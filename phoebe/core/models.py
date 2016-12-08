import json

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from channels import Group


class Zone(models.Model):
    name = models.CharField(max_length=500)
    friendly_name = models.CharField(max_length=500, blank=True, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.friendly_name or self.name


class DeviceGroup(models.Model):
    name = models.CharField(max_length=500)
    friendly_name = models.CharField(max_length=500, default='')
    zone = models.ForeignKey(Zone)

    def __str__(self):
        return self.friendly_name or self.name


class Device(models.Model):
    class Meta:
        unique_together = ("device_group", "name")

    name = models.CharField(max_length=500)
    friendly_name = models.CharField(max_length=500, blank=True, default='')
    device_group = models.ForeignKey(DeviceGroup)
    device_type = models.CharField(max_length=100)

    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    # data received from the device should be stored in here
    data = JSONField(blank=True, default=dict)
    # configuration options for the device (used to update device or interpret data) are stored here
    options = JSONField(blank=True, default=dict)

    def __str__(self):
        return "{} {}".format(self.device_type, self.friendly_name or self.name)

    def save(self, *args, data_source=None, **kwargs):
        super(Device, self).save(*args, **kwargs)

        # If the data didn't come from a device - update the device
        if data_source != 'device':
            # Send update command to any connected websockets for the device's Zone
            zone = self.device_group.zone
            group = Group("user_{}_zone_{}".format(zone.user_id, zone.name))

            group.send({'text': json.dumps({
                'command': 'set_device',
                'device_type': self.device_type,
                'name': self.name,
                'data': self.data
            })})

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class Zone(models.Model):
    name = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name


class DeviceGroup(models.Model):
    name = models.CharField(max_length=500)
    zone = models.ForeignKey(Zone)

    def __str__(self):
        return self.name


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

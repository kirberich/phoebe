import json
import random
import string

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser

from channels import Group
from dirtyfields import DirtyFieldsMixin

from .managers import UserManager


def _generate_api_key():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(8))


class User(AbstractBaseUser):
    objects = UserManager()

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(max_length=255)
    emoji = models.CharField(max_length=100, default='')
    picture_url = models.CharField(max_length=255, blank=True, default='')

    slack_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    in_zone = models.ForeignKey('Zone', blank=True, null=True, related_name='present_users')

    last_seen = models.DateTimeField(default=timezone.now)

    api_key = models.CharField(
        max_length=50,
        default=_generate_api_key
    )

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.nickname or self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin


class Zone(models.Model):
    name = models.CharField(max_length=500)
    friendly_name = models.CharField(max_length=500, blank=True, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.friendly_name or self.name


class DeviceGroup(models.Model):
    name = models.CharField(max_length=500, blank=True)
    friendly_name = models.CharField(max_length=500, default='')
    zone = models.ForeignKey(Zone)

    def __str__(self):
        return self.friendly_name or self.name


class Device(DirtyFieldsMixin, models.Model):
    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=500)
    friendly_name = models.CharField(max_length=500, blank=True, default='')
    groups = models.ManyToManyField(DeviceGroup, blank=True)
    device_type = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    # data received from the device should be stored in here
    data = JSONField(blank=True, default=dict)
    # configuration options for the device (used to update device or interpret data) are stored here
    options = JSONField(blank=True, default=dict)

    def __str__(self):
        groups = [str(group) for group in self.groups.all()]
        pretty_name = self.friendly_name or self.name
        if groups:
            return "{} ({})".format(pretty_name, ", ".join(groups))
        return pretty_name

    def save(self, *args, data_source=None, **kwargs):
        dirty_fields = self.get_dirty_fields()
        super(Device, self).save(*args, **kwargs)

        # If the data didn't come from a device - update the device
        if data_source != 'device' and 'data' in dirty_fields:
            # Send update command to any connected websockets for the device's Zone
            zone = self.device_group.zone
            group = Group("user_{}_zone_{}".format(zone.user_id, zone.name))

            changed_data = {k: v for k, v in self.data.items() if self.data[k] != dirty_fields['data'][k]}

            group.send({'text': json.dumps({
                'command': 'set_state',
                'device_type': self.device_type,
                'name': self.name,
                'data': changed_data
            })})

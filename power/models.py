from ouimeaux.device import switch

from django.db import models

from core.mixins import MultiTableMixin


class Switch(MultiTableMixin):
    home = models.ForeignKey('core.Home', null=True, blank=True)
    room = models.ForeignKey('core.Room', null=True, blank=True)
    name = models.CharField(max_length=255)

    is_on = models.BooleanField()

    def on(self):
        self.is_on = True

    def off(self):
        self.is_on = False


class WeMoSwitch(Switch):
    parent_name = 'Switch'

    device_name = models.CharField(max_length=255)
    device_ip = models.CharField(max_length=255)
    device_mac = models.CharField(max_length=255, blank=True)

    @property
    def xml_url(self):
        return "http://{}:49153/setup.xml".format(self.device_ip)

    @property
    def api(self):
        return switch.Switch(self.xml_url)

    def on(self):
        self.api.on()
        super(WeMoSwitch, self).on()

    def off(self):
        self.api.off()
        super(WeMoSwitch, self).off()


from .signals import *

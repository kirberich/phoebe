from ouimeaux.device import switch

from django.db import models

from core.mixins import MultiTableMixin


class Switch(MultiTableMixin):
    home = models.ForeignKey('core.Home', null=True, blank=True)
    room = models.ForeignKey('core.Room', null=True, blank=True)
    name = models.CharField(max_length=255)

    is_on = models.BooleanField()
    auto_off = models.BooleanField(default=False)
    auto_on = models.BooleanField(default=False)

    def on(self, save=True):
        self.is_on = True
        if save:
            self.save()

    def off(self, save=True):
        self.is_on = False
        if save:
            self.save()

    def update(self):
        if save:
            self.save()

    def handle_event(self, event_type, device):
        if self.auto_off and event_type == constants.EVENT_HOME_VACANT:
            self.off()
        elif self.auto_on and event_type == constants.EVENT_HOME_OCCUPIED:
            self.on()

    def __unicode__(self):
        return self.name


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

    def on(self, save=True):
        self.api.on()
        super(WeMoSwitch, self).on(save=save)

    def off(self, save=True):
        self.api.off()
        super(WeMoSwitch, self).off(save=save)

    def update(self, save=True):
        self.is_on = self.api.get_state()
        super(WeMoSwitch, self).update(save=save)


from .signals import *

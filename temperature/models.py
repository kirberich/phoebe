from django.db import models

from django.conf import settings
import nest as nest_lib

from threading import local
_thread_locals = local()

from core import constants
from core.mixins import MultiTableMixin


class TemperatureController(MultiTableMixin):
    can_sense = False
    can_set = False

    home = models.ForeignKey('core.Home')
    room = models.ForeignKey('core.Room')

    normal_temperature = models.FloatField(default=settings.TEMPERATURE_NORMAL)
    away_temperature = models.FloatField(default=settings.TEMPERATURE_COOL)
    vacation_temperature = models.FloatField(default=settings.TEMPERATURE_COLD)
    warm_temperature = models.FloatField(default=settings.TEMPERATURE_WARM)
    hot_temperature = models.FloatField(default=settings.TEMPERATURE_HOT)

    last_target_temperature = models.FloatField(default=0)
    target_temperature = models.FloatField(default=0)
    current_temperature = models.FloatField(default=0)

    is_in_vacation_mode = models.BooleanField(default=False)
    is_in_away_mode = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    auto_away = models.BooleanField(default=False)

    def set_vacation_mode(self, save=True):
        if not (self.is_in_away_mode or self.is_in_vacation_mode):
            self.last_target_temperature = self.target_temperature

        self.set_target(self.vacation_temperature)
        self.is_in_vacation_mode = True

        if save:
            self.save()

    def set_away_mode(self, save=True):
        if not (self.is_in_away_mode or self.is_in_vacation_mode):
            self.last_target_temperature = self.target_temperature

        self.set_target(self.away_temperature)
        self.is_in_away_mode = True

        if save:
            self.save()

    def set_home_mode(self, save=True):
        self.is_in_vacation_mode = False
        self.is_in_away_mode = False

        if self.last_target_temperature:
            self.set_target(self.last_target_temperature, save=False)
            self.last_target_temperature = 0
        else:
            self.set_target(self.normal_temperature, save=False)

        if save:
            self.save()

    def set_target(self, t, save=True):
        self.target_temperature = t
        if save:
            self.save()

    def update(self, save=True):
        """ Give temperature controller subclasses the chance to update data from an api or sensors or similar. """
        pass

    def status(self):
        if self.is_in_vacation_mode:
            return 'vacation'
        if self.is_in_away_mode:
            return 'away'
        return 'home'


class Nest(TemperatureController):
    parent_name = 'TemperatureController'
    can_sense = True
    can_set = True

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    structure_name = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, blank=True)

    @property
    def api(self):
        """ Add a lazy interface for accessing the api """
        key = 'nest_api_{}'.format(self.pk)
        if self.pk and hasattr(_thread_locals, key):
            return getattr(_thread_locals, key)

        _api = nest_lib.Nest(self.username, self.password, cache_ttl=60)
        setattr(_thread_locals, key, _api)
        return _api

    @property
    def device(self):
        return [d for d in self.api.devices if d.name == self.device_name][0] if self.device_name else self.api.devices[0]

    @property
    def structure(self):
        return [s for s in self.api.structures if s.name == self.structure_name][0] if self.structure_name else self.api.structures[0]

    def set_vacation_mode(self, save=True):
        self.structure.away = True
        super(Nest, self).set_vacation_mode(save=save)

    def set_home_mode(self, save=True):
        self.structure.away = False
        super(Nest, self).set_home_mode(save=save)

    def update(self, save=True):
        self.current_temperature = self.device.temperature
        self.target_temperature = self.device.target
        self.is_in_vacation_mode = self.structure.away
        self.is_active = self.device.hvac_heater_state

        if save:
            self.save()

    def set_target(self, t, save=True):
        self.device.temperature = t
        super(Nest, self).set_target(t, save=save)

    def handle_event(self, event_type, device):
        if self.auto_away and event_type == constants.EVENT_HOME_VACANT:
            self.set_away_mode()
        elif self.auto_away and event_type == constants.EVENT_HOME_OCCUPIED:
            self.set_home_mode()

from .signals import *

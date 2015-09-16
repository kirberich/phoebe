from django.db import models
from django.core.cache import cache

from jsonfield.fields import JSONField
from slacker import Slacker

from core.mixins import MultiTableMixin
from core import constants


class Notifier(MultiTableMixin):
    # Notifiers can have a home, in which case they only notify about events in that home.
    home = models.ForeignKey('core.Home', blank=True, null=True)
    react_to = JSONField(blank=True)

    def send(self, message):
        raise NotImplementedError()

    def handle_event(self, event_type, device):
        if event_type not in self.react_to:
            return

        if event_type == constants.EVENT_USER_HOME:
            self.send("{} just came home!".format(device.user))
        elif event_type == constants.EVENT_USER_AWAY:
            self.send("{} just left!".format(device.user))
        elif event_type == constants.EVENT_HOME_VACANT:
            self.send("{} is now vacant.".format(device.home))
        elif event_type == constants.EVENT_HOME_OCCUPIED:
            self.send("{} is now occupied.".format(device.home))


class Slack(Notifier):
    parent_name = "Notifier"
    api_key = models.CharField(max_length=255)
    channel = models.CharField(max_length=255)
    username = models.CharField(max_length=255, default='Phoebe')
    icon = models.URLField(max_length=500, default='https://i2.wp.com/s3.amazonaws.com/rapgenius/d43e2b45855a8bde06330c076628b2a7.jpeg')

    @property
    def api(self):
        cache_key = 'slack-api-{}'.format(self.pk)
        cached_api = cache.get(cache_key)
        if cached_api:
            return cached_api

        if not self.api_key:
            raise Exception("Slack notifier doesn't have an api key set.")

        api = Slacker(self.api_key)
        cache.set(cache_key, api, 60*60*24)
        return api

    def send(self, message):
        return self.api.chat.post_message(self.channel, message, username=self.username, icon_url=self.icon)


from .signals import *

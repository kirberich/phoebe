import logging

from django.dispatch import (
    Signal,
    receiver,
)

from core.models import Plugin


# Custom signal to model phoebe events, which occur any time a device changes state, or when triggered by a command.
event = Signal(providing_args=['event_type', 'zone', 'user', 'data'])


@receiver(event)
def trigger_plugins(sender, **kwargs):
    """Everytime an event occurs, run all acrive plugins."""
    plugins = Plugin.objects.filter(is_active=True)
    for plugin in plugins:
        try:
            plugin.run(
                sender,
                kwargs['event_type'],
                kwargs['zone'],
                kwargs['user'],
                kwargs['data'],
            )
        except:
            # Catch and log all exceptions as we don't want a broken plugin bringing down the app
            logging.exception("Something went wrong trying to run a plugin")

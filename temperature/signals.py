from django.dispatch import receiver

from core import constants
from core.signals import automation_event
from .models import TemperatureController


@receiver(automation_event)
def on_mode_change(sender, **kwargs):
    home = kwargs['home']
    event_type = kwargs['event_type']
    device = kwargs['device']

    if event_type not in [constants.EVENT_HOME_VACANT, constants.EVENT_HOME_OCCUPIED]:
        return

    controllers = [c.get_child() for c in TemperatureController.objects.filter(home=home, auto_away=True)]

    for controller in controllers:
        controller.handle_event(event_type, device)

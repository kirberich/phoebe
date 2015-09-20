from celery import shared_task

from django.db.models.signals import post_save
from django.dispatch import receiver

from core import constants
from core.models import Device
from core.signals import automation_event
from .models import Switch, WeMoSwitch


@receiver(post_save, sender=WeMoSwitch)
def power_change(sender, instance, *args, **kwargs):
    instance.api.set_state(instance.is_on)
    event_type = 'power_on' if instance.is_on else 'power_off'
    automation_event.send(sender=sender, home=instance.home, event_type=event_type, device=instance)


@shared_task
def deferred_handle_event(switch_id, event_type, device_id):
    switch = Switch.objects.get(id=switch_id).get_child()
    device = Device.objects.get(id=device_id)
    switch.handle_event(event_type, device)

@receiver(automation_event)
def on_mode_change(sender, **kwargs):
    home = kwargs['home']
    event_type = kwargs['event_type']
    device = kwargs['device']

    if event_type not in [constants.EVENT_HOME_VACANT, constants.EVENT_HOME_OCCUPIED]:
        return

    switches = [n.get_child() for n in Switch.objects.filter(home=home)]

    for switch in switches:
        deferred_handle_event.delay(switch.id, event_type, device.id)

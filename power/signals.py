from django.db.models.signals import post_save
from django.dispatch import receiver

from core.signals import automation_event
from .models import WeMoSwitch


@receiver(post_save, sender=WeMoSwitch)
def power_change(sender, instance, *args, **kwargs):
    instance.api.set_state(instance.is_on)
    event_type = 'power_on' if instance.is_on else 'power_off'
    automation_event.send(sender=sender, home=instance.home, event_type=event_type, device=instance)

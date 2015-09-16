from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver, Signal

from models import Device
from . import constants


automation_event = Signal(providing_args=['event_type', 'home', 'device'])


@receiver(pre_save, sender=Device)
def device_pre_save(sender, instance, *args, **kwargs):
    if "is_present" not in instance.get_dirty_fields():
        return

    if not instance.is_present and not Device.objects.filter(user_id=instance.user_id, is_present=True).exclude(pk=instance.pk).exists():
        automation_event.send(sender=sender, home=instance.home, event_type=constants.EVENT_HOME_VACANT, device=instance)

    if instance.is_present and not Device.objects.filter(user_id=instance.user_id, is_present=False).exclude(pk=instance.pk).exists():
        automation_event.send(sender=sender, home=instance.home, event_type=constants.EVENT_HOME_OCCUPIED, device=instance)


@receiver(post_save, sender=Device)
def _device_post_save(sender, instance, *args, **kwargs):
    if "is_present" in instance.get_dirty_fields():
        event_type = constants.EVENT_USER_HOME if instance.is_present else constants.EVENT_USER_AWAY
        automation_event.send(sender=sender, home=instance.home, event_type=event_type, device=instance)

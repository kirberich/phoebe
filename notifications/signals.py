from django.db.models import Q
from django.dispatch import receiver

from core.signals import automation_event

from .models import Notifier


@receiver(automation_event)
def on_event(sender, **kwargs):
    home = kwargs['home']
    event_type = kwargs['event_type']
    device = kwargs['device']

    # Get notifiers that care about this event
    notifiers = [n.get_child() for n in Notifier.objects.filter(Q(react_to__contains=event_type), (Q(home=home) | Q(home=None)))]

    for notifier in notifiers:
        notifier.handle_event(event_type, device)

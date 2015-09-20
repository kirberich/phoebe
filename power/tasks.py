from celery import shared_task

from .models import Switch


@shared_task
def update_switch_states():
    switches = [n.get_child() for n in Switch.objects.all()]

    for switch in switches:
        switch.update()

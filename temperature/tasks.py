from celery import shared_task

from .models import TemperatureController

@shared_task
def update_temperatures():
    controllers = [c.get_child() for c in TemperatureController.objects.all()]
    for c in controllers:
        c.update()

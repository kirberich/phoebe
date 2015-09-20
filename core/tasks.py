from billiard import Process
from celery import shared_task

from . import presence
from .models import Device
from .locking import acquire_lock


@shared_task
def check_user_presence():
    for device in Device.objects.all():
        lock_id = 'scan-device-lock-{}'.format(device.id)
        if acquire_lock(lock_id):
            t = Process(target=presence.scan_device, args=(device, lock_id))
            t.start()

    return "ok"

from billiard import Process

from django.core.cache import cache
from django.utils.timezone import now, timedelta

from .models import Device

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes
PRESENCE_TIMEOUT = timedelta(minutes=1)

acquire_lock = lambda lock_id: cache.add(lock_id, 'true', LOCK_EXPIRE)
release_lock = lambda lock_id: cache.delete(lock_id)


def scan_device(device, timeout):
    # For some reason django's database handling freaks out when running this in a thread,
    # restarting the database connection fixes it though.
    from django.db import connection
    connection.close()

    lock_id = 'scan-device-lock-{}'.format(device.id)
    if not acquire_lock(lock_id):
        return

    try:
        is_present = device.ping(timeout=timeout)

        # Pinging can take a while, so reload the object afterwards
        device = Device.objects.get(pk=device.pk)

        if is_present:
            device.is_present = True
            device.last_seen = now()
        elif device.is_present and now() - device.last_seen > PRESENCE_TIMEOUT:
            device.is_present = False

        device.save()
    finally:
        release_lock(lock_id)


def check_user_presence():
    for device in Device.objects.all():
        if now() - device.last_scanned > timedelta(seconds=60):
            device.last_scanned = now()
            device.save()

            t = Process(target=scan_device, args=(device, PRESENCE_TIMEOUT.total_seconds()))
            t.start()

    return "ok"

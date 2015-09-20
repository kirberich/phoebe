import time

from django.utils.timezone import now, timedelta

from .models import Device
from .locking import refresh_lock, release_lock

PRESENCE_TIMEOUT = timedelta(hours=2)
PING_TIMEOUT = timedelta(minutes=2)


def scan_device(device, lock_id):
    # For some reason django's database handling freaks out when running this in a thread,
    # restarting the database connection fixes it though.
    from django.db import connection
    connection.close()

    try:
        while Device.objects.filter(id=device.pk).exists():
            # Refresh the lock to show this scan is still running
            refresh_lock(lock_id)

            start_time = now()
            is_present = device.ping(timeout=PING_TIMEOUT.total_seconds())

            # Pinging can take a long time, so reload the object afterwards
            device = Device.objects.get(pk=device.pk)

            if is_present:
                device.is_present = True
                device.last_scanned = now()
                device.last_seen = now()
            elif device.is_present and now() - device.last_seen > PRESENCE_TIMEOUT:
                device.is_present = False

            device.save()

            end_time = now()
            if is_present and end_time - start_time < PING_TIMEOUT:
                time.sleep((PING_TIMEOUT - (end_time - start_time)).total_seconds())
    finally:
        release_lock(lock_id)

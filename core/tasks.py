from celery import shared_task

from . import presence

@shared_task
def check_user_presence():
    return presence.check_user_presence()

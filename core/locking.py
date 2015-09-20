from django.core.cache import cache


LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


def acquire_lock(lock_id, expire=LOCK_EXPIRE):
    return cache.add(lock_id, 'true', LOCK_EXPIRE)


def refresh_lock(lock_id, expire=LOCK_EXPIRE):
    return cache.set(lock_id, 'true', LOCK_EXPIRE)


def release_lock(lock_id):
    return cache.delete(lock_id)

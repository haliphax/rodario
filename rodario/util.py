""" Utility module for rodario framework """

# stdlib
from time import time
# local
from rodario import get_redis_connection


def acquire_lock(name, expiry=None, context=None, conn=None):
    """
    Acquire a lock in redis.

    :param str name: Name of the lock to acquire
    :param int expiry: The duration of the lock (in seconds)
    :param str context: The context to apply to the lock name
    :param redis.Connection conn: The redis connection to use
    :rtype: :class:`bool`
    :returns: Whether or not the lock was acquired
    """

    # pylint: disable=W0212
    current = time()
    lock_expiry = 3 if expiry is None else expiry
    lock_expires = current + lock_expiry
    lock_context = 'global.lock' if context is None else context
    lock_name = '%s:%s' % (lock_context, name)
    redis = get_redis_connection() if conn is None else conn

    # try to get lock; if we fail, do sanity check on lock
    if not redis.setnx(lock_name, lock_expires):
        # see if current lock is expired; if so, take it
        if current < float(redis.get(lock_name)):
            # lock is not expired
            return False
        elif current < float(redis.getset(lock_name, lock_expires)):
            # somebody else beat us to it
            return False

    # we have the lock; give it a TTL and pass through
    redis.expire(lock_name, lock_expiry)

    return True

""" Actor registry for rodario framework """

# local
from rodario import get_redis_connection
from rodario.exceptions import RegistrationException


# pylint: disable=C1001
class _RegistrySingleton(object):

    """ Singleton for actor registry """

    def __init__(self, prefix=None):
        """
        Initialize the registry.

        :param str prefix: Optional prefix for redis key names
        """

        self._redis = get_redis_connection()
        self._list = '{prefix}actors'.format(prefix=prefix)

    @property
    def actors(self):
        """
        Retrieve a list of registered actors.

        :rtype: :class:`set`
        """

        return self._redis.smembers(self._list)

    def register(self, uuid):
        """
        Register a new actor.

        :param str uuid: The UUID of the actor to register
        """

        if self._redis.sadd(self._list, uuid) == 0:
            raise RegistrationException('Failed adding member to set')

    def unregister(self, uuid):
        """
        Unregister an existing actor.

        :param str uuid: The UUID of the actor to unregister
        """

        self._redis.srem(self._list, uuid)

    def exists(self, uuid):
        """
        Test whether an actor exists in the registry.

        :param str uuid: UUID of the actor to check for
        :rtype: :class:`bool`
        """

        return self._redis.sismember(self._list, uuid) == 1

    # pylint: disable=R0201
    def get_proxy(self, uuid):
        """
        Return an ActorProxy for the given UUID.

        :param str uuid: The UUID to return a proxy object for
        :rtype: :class:`rodario.actors.ActorProxy`
        """

        # avoid cyclic import
        proxy_module = __import__('rodario.actors',
                                  fromlist=('ActorProxy',))

        return proxy_module.ActorProxy(uuid=uuid)


# pylint: disable=R0903
class Registry(object):

    """ Actor registry class (singleton wrapper) """

    _instance = None

    def __new__(cls, prefix=None):
        """
        Retrieve the singleton instance for Registry.

        :param str prefix: Optional prefix for redis key names
        :rtype: :class:`rodario.registry._RegistrySingleton`
        """

        if not cls._instance:
            cls._instance = _RegistrySingleton(prefix=prefix)

        return cls._instance

""" Actor registry for rodario framework """

# 3rd party
import redis

# local
from rodario.exceptions import RegistrationException


# pylint: disable=C1001
class _RegistrySingleton(object):

    """ Singleton for actor registry """

    def __init__(self):
        """ Initialize the registry. """

        self._redis = redis.StrictRedis()

    @property
    def actors(self):
        """
        Retrieve a list of registered actors.

        :rtype: :class:`set`
        """

        return self._redis.smembers('actors')

    def register(self, uuid):
        """
        Register a new actor.

        :param str uuid: The UUID of the actor to register
        """

        if self._redis.sadd('actors', uuid) == 0:
            raise RegistrationException('Failed adding member to set')

    def unregister(self, uuid):
        """
        Unregister an existing actor.

        :param str uuid: The UUID of the actor to unregister
        """

        self._redis.srem('actors', uuid)

    def exists(self, uuid):
        """
        Test whether an actor exists in the registry.

        :param str uuid: UUID of the actor to check for
        :rtype: :class:`bool`
        """

        return self._redis.sismember('actors', uuid) == 1

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

    def __new__(cls):
        """
        Retrieve the singleton instance for Registry.

        :rtype: :class:`rodario.registry._RegistrySingleton`
        """

        if not cls._instance:
            cls._instance = _RegistrySingleton()

        return cls._instance

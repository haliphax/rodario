""" Actor for rodario framework """

# stdlib
import atexit
from uuid import uuid4
from time import sleep
from threading import Thread, Event
import pickle
import inspect

# 3rd party
import redis

# local
from rodario.registry import Registry

REGISTRY = Registry()


# pylint: disable=I0011,E1101
class Actor(object):

    """ Base Actor class """

    #: Threading Event to tell the message handling loop to die
    # (needed in __del__ so must be defined here)
    _stop = None

    def __init__(self, uuid=None):
        """
        Initialize the Actor object.

        :param str uuid: Optionally-provided UUID
        """

        atexit.register(self.__del__)
        self._stop = Event()
        #: Separate Thread for handling messages
        self._proc = None
        #: Redis connection
        self._redis = redis.StrictRedis()
        #: Redis PubSub client
        self._pubsub = None

        # pylint: disable=I0011,E1123
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)

        if uuid:
            self.uuid = uuid
        else:
            self.uuid = str(uuid4())

        if not REGISTRY.exists(self.uuid):
            REGISTRY.register(self.uuid)
        else:
            self.uuid = None
            raise Exception('UUID is already taken')

    def __del__(self):
        """ Clean up. """

        if hasattr(self, 'uuid'):
            REGISTRY.unregister(self.uuid)

        self.stop()

    @property
    def is_alive(self):
        """
        Return True if this Actor is still alive.

        :rtype: :class:`bool`
        """

        return not self._stop.is_set()

    def _handler(self, message):
        """
        Send proxied method call results back through pubsub.

        :param tuple message: The message to dissect
        """

        data = pickle.loads(message['data'])

        if not data[1]:
            # empty method call; bail out
            return

        # call the function and respond to the proxy object with return value
        proxy = data[0]
        queue = data[1]
        func = getattr(self, data[2])
        result = (queue, func(*data[3], **data[4]),)
        self._redis.publish('proxy:%s' % proxy, pickle.dumps(result))

    def _get_methods(self):
        """
        List all of this Actor's methods (for creating remote proxies).

        :rtype: :class:`list`
        """

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        method_list = []

        for name, _ in methods:
            if (name in ('proxy', '_get_methods', 'start', 'stop',)
                    or name[0] == '_'):
                continue

            method_list.append(name)

        return method_list

    def proxy(self):
        """
        Wrap this Actor in an ActorProxy object.

        :rtype: :class:`rodario.actors.ActorProxy`
        """

        # avoid cyclic import
        proxy_module = __import__('rodario.actors', fromlist=('ActorProxy',))

        return proxy_module.ActorProxy(self)

    def start(self):
        """ Fire up the message handler thread. """

        def pubsub_thread():
            """ Call get_message in loop to fire _handler. """

            while not self._stop.is_set():
                self._pubsub.get_message()
                sleep(0.01)

        # subscribe to personal channel and fire up the message handler
        self._pubsub.subscribe(**{'actor:%s' % self.uuid: self._handler})
        self._proc = Thread(target=pubsub_thread)
        self._proc.daemon = True
        self._proc.start()

    def stop(self):
        """ Kill the message handler thread. """

        self._stop.set()

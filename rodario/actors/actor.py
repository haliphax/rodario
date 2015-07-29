""" Actor for rodario framework """

# stdlib
from uuid import uuid4
from time import sleep
from threading import Thread, Event
import pickle
import inspect

# 3rd party
import redis

# local
import rodario.actors


class Actor(object):

    """ Base Actor class """

    def __init__(self, uuid=None):
        """
        Initialize the Actor object.

        :param str uuid: Optionally-provided UUID
        """

        #: Threading Event to tell the message handling loop to die
        self._stop = Event()
        #: Separate Thread for handling messages
        self._proc = None
        #: Redis connection
        self.redis = redis.StrictRedis()
        # pylint: disable=I0011,E1123
        #: Redis PubSub client
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

        if uuid:
            # if custom UUID is provided, check for existence first
            if self.redis.publish('actor:%s' % uuid, None):
                raise Exception('Actor exists')

            self.uuid = uuid
        else:
            self.uuid = str(uuid4())

    def __del__(self):
        """ Clean up. """

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
        self.redis.publish('proxy:%s' % proxy, pickle.dumps(result))

    def get_methods(self):
        """
        List all of this Actor's methods (for creating remote proxies).

        :rtype: :class:`list`
        """

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        method_list = []

        for name, _ in methods:
            if (name in ('proxy', 'get_methods', 'start', 'stop',)
                    or name[0] == '_'):
                continue

            method_list.append(name)

        return method_list

    def proxy(self):
        """
        Wrap this Actor in an ActorProxy object.

        :rtype: :class:`rodario.actors.ActorProxy`
        """

        return rodario.actors.ActorProxy(self)

    def start(self):
        """ Fire up the message handler thread. """

        def pubsub_thread(pubsub):
            """ Call get_message in loop to fire _handler. """

            try:
                while not self._stop.is_set():
                    pubsub.get_message()
                    sleep(0.01)
            except:  # pylint: disable=I0011,W0702
                pass

        # subscribe to personal channel and fire up the message handler
        self.pubsub.subscribe(**{'actor:%s' % self.uuid: self._handler})
        self._proc = Thread(target=pubsub_thread, args=(self.pubsub,))
        self._proc.daemon = True
        self._proc.start()

    def stop(self):
        """ Kill the message handler thread. """

        self._stop.set()

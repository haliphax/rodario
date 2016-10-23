""" Cluster Proxy for rodario framework """

# stdlib
import pickle
import types
from multiprocessing import Queue, Event
from threading import Thread
from time import sleep
from uuid import uuid4

# 3rd party
import redis

# local
from rodario.future import Future
from rodario.exceptions import EmptyClusterException


# pylint: disable=R0903
class ClusterProxy(object):

    """
    Proxy object responsible for multiple actors

    This class is meant to be inherited by child objects which can provide
    their own API methods for coordinating the Actors in their channel.
    """

    #: Flag for Stopping the message handler thread
    _stop = None

    def __init__(self, channel):
        """
        Initialize instance of ClusterProxy.

        :param str channel: The cluster channel to use
        """

        #: Cluster channel
        self.channel = channel
        #: Redis connection
        self._redis = redis.StrictRedis()
        #: Redis PubSub client
        self._pubsub = None
        #: This proxy object's UUID for creating unique channels
        self.proxyid = str(uuid4())
        #: Response queues for sandboxing method calls
        self._response_queues = {}
        #: Response counters for the response queue
        self._response_counters = {}
        self._stop = Event()
        # pylint: disable=E1123
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(**{'proxy:%s' % self.proxyid: self._handler})

        def pubsub_thread():
            """ Call get_message in loop to fire _handler. """

            try:
                while not self._stop.is_set():
                    self._pubsub.get_message()
                    sleep(0.001)
            except:  # pylint: disable=W0702
                pass

        # fire up the message handler thread as a daemon
        proc = Thread(target=pubsub_thread)
        proc.daemon = True
        proc.start()

    def __getattribute__(self, name):
        """
        Return transparent callables for everything and proxy the calls.

        :param str name: Name of the attribute being requested
        :rtype: lambda
        """

        def get_lambda(name):
            """
            Create a proxied callable.

            :param str name: Name of the callable to wrap
            :rtype: instancemethod
            """

            return lambda _, *args, **kwargs: self._proxy(name, *args, **kwargs)

        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return types.MethodType(get_lambda(name), self)

    def _handler(self, message):
        """
        Handle message response via Queue object.

        :param tuple message: The message to dissect
        """

        # throw its value in the associated response queue
        data = pickle.loads(message['data'])

        if data[1] != False:
            queue = self._response_queues[data[0]]
            queue.put(data[1])
            self._response_queues[data[0]] = queue

        self._response_counters[data[0]] -= 1

        if self._response_counters[data[0]] <= 0:
            self._response_queues.pop(data[0])

    def _proxy(self, method_name, *args, **kwargs):
        """
        Proxy a method call to redis pubsub.

        Use this method in your child objects which inherit from ClusterProxy
        to provide the proxy with some representation of the public API for the
        Actors it represents.

        :paramstr method_name: The method to proxy
        :param tuple args: The arguments to pass
        :param dict kwargs: The keyword arguments to pass
        :rtype: :class:`rodario.future.Future`
        :returns: A Future whose first value is the number of expected responses
        """

        uuid = str(uuid4())
        data = (uuid, self.proxyid, method_name, args, kwargs,)
        # fire off the method call to the original Actors over pubsub
        count = self._redis.publish('cluster:%s' % self.channel,
                                    pickle.dumps(data))

        if count == 0:
            raise EmptyClusterException()

        queue = Queue()
        queue.put(count)
        self._response_queues[uuid] = queue
        self._response_counters[uuid] = count

        return Future(queue)

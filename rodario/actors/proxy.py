""" Actor proxy for rodario framework """

# stdlib
import types
import pickle
from multiprocessing import Queue
from threading import Thread
from uuid import uuid4
from time import sleep

# 3rd party
import redis

# local
from rodario.future import Future
from rodario.exceptions import InvalidActorException, InvalidProxyException


class ActorProxy(object):  # pylint: disable=R0903

    """ Proxy object that fires calls to an actor over redis pubsub """

    def __init__(self, actor=None, uuid=None):
        """
        Initialize instance of ActorProxy.

        Accepts either an Actor object to clone or a UUID, but not both.

        :param rodario.actors.Actor actor: Actor to clone
        :param str uuid: UUID of Actor to clone
        """

        #: Redis connection
        self._redis = redis.StrictRedis()
        #: Redis PubSub client
        self._pubsub = None
        #: This proxy object's UUID for creating unique channels
        self.proxyid = str(uuid4())
        #: Response queues for sandboxing method calls
        self._response_queues = {}
        # avoid cyclic import
        actor_module = __import__('rodario.actors', fromlist=('Actor',))
        # pylint: disable=E1123
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(**{'proxy:%s' % self.proxyid: self._handler})
        # list of blocking methods
        self._blocking_methods = set()

        methods = set()

        def pubsub_thread():
            """ Call get_message in loop to fire _handler. """

            try:
                while self._pubsub:
                    self._pubsub.get_message()
                    sleep(0.001)
            except:  # pylint: disable=W0702
                pass

        # fire up the message handler thread as a daemon
        proc = Thread(target=pubsub_thread)
        proc.daemon = True
        proc.start()

        if isinstance(actor, actor_module.Actor):
            # proxying an Actor directly
            self.uuid = actor.uuid
            methods = actor._get_methods()  # pylint: disable=W0212
        elif isinstance(uuid, str):
            # proxying by UUID; get actor methods over pubsub
            self.uuid = uuid
            methods = self._proxy('_get_methods').get()
        else:
            raise InvalidProxyException('No actor or UUID provided')

        def get_lambda(name):
            """
            Generate a lambda function to proxy the given method.

            :param str name: Name of the method to proxy
            :rtype: :expression:`lambda`
            """

            return lambda _, *args, **kwargs: self._proxy(name, *args, **kwargs)

        # create proxy methods for each public method of the original Actor
        for name in methods:
            name_split = name.split(':')

            for attr in name_split[1:]:
                if attr == 'blocking':
                    self._blocking_methods.add(name_split[0])

            setattr(self, name_split[0],
                    types.MethodType(get_lambda(name_split[0]), self))

    def _handler(self, message):
        """
        Handle message response via Queue object.

        :param tuple message: The message to dissect
        """

        # throw its value in the associated response queue
        data = pickle.loads(message['data'])
        self._response_queues[data[0]].put(data[1])
        self._response_queues.pop(data[0])

    def _proxy(self, method_name, *args, **kwargs):
        """
        Proxy a method call to redis pubsub.

        This method is not meant to be called directly. Instead, it is used
        by the proxy's self-generated methods to provide the proxy with the
        same public API as the actor it represents.

        :param str method_name: The method to proxy
        :param tuple args: The arguments to pass
        :param dict kwargs: The keyword arguments to pass
        :rtype: :class:`multiprocessing.Queue`
        """

        # fire off the method call to the original Actor over pubsub
        uuid = str(uuid4())
        count = self._redis.publish('actor:%s' % self.uuid,
                                    pickle.dumps((uuid, self.proxyid,
                                                  method_name, args, kwargs,)))

        if count == 0:
            raise InvalidActorException('No such actor')

        queue = Queue()
        self._response_queues[uuid] = queue

        if method_name in self._blocking_methods:
            return queue.get()

        return Future(queue)

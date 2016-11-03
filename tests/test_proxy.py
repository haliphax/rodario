""" ActorProxy unit tests for rodario framework """

# stdlib
import unittest
from time import sleep

# local
from rodario.registry import Registry
from rodario.actors import Actor, ActorProxy
from rodario.future import Future
from rodario.exceptions import InvalidActorException, InvalidProxyException


# pylint: disable=R0201
class TestActor(Actor):

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1

    def delay(self):
        """ Delayed method call for testing ready property of Future. """

        sleep(1)

        return 1


# pylint: disable=C0103,R0904
class ProxyTests(unittest.TestCase):

    """ ActorProxy unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor and an ActorProxy for it. """

        cls.registry = Registry()
        cls.actor = TestActor(uuid='noexist_proxy')
        cls.actor.start()
        cls.proxy = cls.actor.proxy()

    @classmethod
    def tearDownClass(cls):
        """ Kill the Actor. """

        cls.actor.stop()
        cls.registry.unregister('noexist_proxy')  # pylint: disable=E1101

    def testNoParametersInConstructor(self):
        """
        Raise InvalidProxyException when no constructor parameters are passed.
        """

        self.assertRaises(InvalidProxyException, ActorProxy)

    def testUUIDConstructor(self):
        """ Create a proxy for a given UUID. """

        proxy = ActorProxy(uuid='noexist_proxy')
        self.assertEqual('noexist_proxy', proxy.uuid)

    def testMethodExists(self):
        """ Ensure that the 'test' method of MyActor has been proxied. """

        self.assertTrue(getattr(self.proxy, 'test') is not None)

    def testActorUUID(self):
        """ Validate the UUID of the underlying Actor. """

        self.assertEqual('noexist_proxy', self.proxy.uuid)

    def testProxyResponseIsFuture(self):
        """ Validate that the object returned from a proxy call is a Future. """

        response = self.proxy.test()  # pylint: disable=E1101
        self.assertTrue(isinstance(response, Future))
        response.get(timeout=1)

    def testProxyDelayedFuture(self):
        """ Validate that the ready property of the Future is accurate. """

        response = self.proxy.delay()
        self.assertFalse(response.ready)
        response.get(timeout=2)

    def testProxyCallAndResponse(self):
        """ Validate the return value of MyActor.test. """

        # pylint: disable=E1101
        response = self.proxy.test().get(timeout=1)
        self.assertEqual(1, response)

    def testInvalidProxy(self):
        """ Raise InvalidActorException when proxying to an invalid actor. """

        newactor = Actor()
        falseproxy = newactor.proxy()
        del newactor
        # pylint: disable=W0212
        self.assertRaises(InvalidActorException, falseproxy._proxy, None)

    def testMissingPubSub(self):
        """ Fail silently when _pubsub is deleted (simulates shutdown). """

        newactor = Actor()
        newactor.start()
        proxy = newactor.proxy()
        del proxy._pubsub

if __name__ == '__main__':
    unittest.main()

""" ActorProxy unit tests for rodario framework """

# stdlib
import unittest
import pickle
import multiprocessing.queues

# 3rd party
import redis

# local
from rodario.actors import Actor, ActorProxy


class TestActor(Actor):

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1


class ProxyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.actor = TestActor(uuid='noexist_proxy')
        cls.actor.start()
        cls.proxy = cls.actor.proxy()

    @classmethod
    def tearDownClass(cls):
        cls.actor.stop()

    def testMethodExists(self):
        self.assertTrue(getattr(self.proxy, 'test') is not None)

    def testActorUUID(self):
        self.assertEqual('noexist_proxy', self.proxy.uuid)

    def testProxyResponseIsQueue(self):
        response = self.proxy.test()
        self.assertEqual(multiprocessing.queues.Queue, type(response))
        response.get()

    def testProxyCallAndResponse(self):
        response = self.proxy.test().get()
        self.assertEqual(1, response)


if __name__ == '__main__':
    unittest.main()

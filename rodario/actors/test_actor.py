""" Actor unit tests for rodario framework """

# stdlib
import unittest
import pickle

# 3rd party
import redis

# local
from rodario.registry import Registry
from rodario.actors import Actor
from rodario.exceptions import UUIDInUseException


class ActorTestActor(Actor):
    # pylint: disable=R0201

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1

    def another_method(self):
        """ Secondary method. """

        return 2


class ActorTests(unittest.TestCase):
    # pylint: disable=R0904,C0103,W0212

    """ Actor unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor object, redis connection, and pubsub client. """

        cls.registry = Registry()
        cls.actor = ActorTestActor('noexist_actor')
        cls.actor.start()
        cls.redis = redis.StrictRedis()
        cls.pubsub = cls.redis.pubsub()

    @classmethod
    def tearDownClass(cls):
        """ Kill the actor. """

        cls.actor.stop()
        cls.registry.unregister('noexist_actor')  # pylint: disable=E1101

    def testGeneratedUUID(self):
        """ Create an actor with an automatically-generated UUID. """

        actor = ActorTestActor()
        self.assertTrue(isinstance(actor.uuid, str))

    def testTakenUUID(self):
        """ Raise UUIDInUseException when uuid is already taken. """

        self.assertRaises(UUIDInUseException, ActorTestActor,
                          **{'uuid': 'noexist_actor'})

    def testMethodCall(self):
        """ Call the Actor's methods. """

        self.assertEqual(1, self.actor.test())
        self.assertEqual(2, self.actor.another_method())

    def testEmptyMethod(self):
        """ Pass a blank method to the actor. """

        self.assertIsNone(self.actor._handler({'data': pickle.dumps((None,
                                                                     None,
                                                                     None,
                                                                     None,))}))

    def testIsAlive(self):
        """ Verify is_alive returns True. """

        self.assertEqual(True, self.actor.is_alive)
        self.actor.stop()

    def testGetMethods(self):
        """ Verify that _get_methods returns the expected list. """

        self.assertEqual(set(['another_method', 'test']),
                         self.actor._get_methods())

    def testHandler(self):
        """ Verify that the Actor is responding to proxied method calls. """

        self.pubsub.subscribe('proxy:noexist_actor')
        count = self.redis.publish('actor:noexist_actor',
                                   ('noexist_actor', 'test', (), {}))
        self.assertEqual(1, count)
        message = self.pubsub.get_message()  # pylint: disable=E1101
        self.assertEqual(message['channel'], 'proxy:noexist_actor')
        self.assertEqual(1, message['data'])
        self.pubsub.unsubscribe('proxy:noexist_actor')

    def testChannel(self):
        """ Join and part a cluster channel. """

        def handler(self, message):  # pylint: disable=W0613
            """ Handle message. """

            return True

        self.actor.join('cluster_test', handler)
        count = self.redis.publish('cluster:cluster_test', 1)
        self.assertEqual(1, count)
        self.actor.part('cluster_test')
        count = self.redis.publish('cluster:cluster_test', 1)
        self.assertEqual(0, count)


if __name__ == '__main__':
    unittest.main()

""" Actor unit tests for rodario framework """

# stdlib
import unittest
import pickle

# 3rd party
import redis

# local
from rodario.actors import Actor


class TestActor(Actor):

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1

    def another_method(self):
        """ Secondary method. """

        return 2


class ActorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.actor = TestActor('noexist_actor')
        cls.actor.start()
        cls.redis = redis.StrictRedis()
        cls.pubsub = cls.redis.pubsub()

    @classmethod
    def tearDownClass(cls):
        cls.actor.stop()

    def testTakenUUID(self):
        self.assertRaises(Exception, TestActor, **{'uuid': 'noexist_actor'})

    def testMethodCall(self):
        self.assertEqual(1, self.actor.test())
        self.assertEqual(2, self.actor.another_method())

    def testIsAlive(self):
        self.assertEqual(True, self.actor.is_alive)
        self.actor.stop()

    def testGetMethods(self):
        self.assertEqual(['another_method', 'test'], self.actor.get_methods())

    def testHandler(self):
        self.pubsub.subscribe('proxy:noexist_actor')
        count = self.redis.publish('actor:noexist_actor',
                                   ('noexist_actor', 'test', (), {}))
        self.assertEqual(1, count)
        message = self.pubsub.get_message()
        self.assertEqual(message['channel'], 'proxy:noexist_actor')
        self.assertEqual(1, message['data'])
        self.pubsub.unsubscribe('proxy:noexist_actor')


if __name__ == '__main__':
    unittest.main()

""" Actor unit tests for rodario framework """

# stdlib
import unittest

# 3rd party
import redis

# local
from rodario.actors import Actor

# pylint: disable=I0011,R0201

class TestActor(Actor):

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1

    def another_method(self):
        """ Secondary method. """

        return 2


# pylint: disable=I0011,R0904,C0103
class ActorTests(unittest.TestCase):

    """ Actor unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor object, redis connection, and pubsub client. """

        cls.actor = TestActor('noexist_actor')
        cls.actor.start()
        cls.redis = redis.StrictRedis()
        cls.pubsub = cls.redis.pubsub()

    @classmethod
    def tearDownClass(cls):
        """ Kill the actor. """

        cls.actor.stop()

    def testTakenUUID(self):
        """ Raise Exception when uuid is already taken. """

        self.assertRaises(Exception, TestActor, **{'uuid': 'noexist_actor'})

    def testMethodCall(self):
        """ Call the Actor's methods. """

        self.assertEqual(1, self.actor.test())
        self.assertEqual(2, self.actor.another_method())

    def testIsAlive(self):
        """ Verify is_alive returns True. """

        self.assertEqual(True, self.actor.is_alive)
        self.actor.stop()

    def testGetMethods(self):
        """ Verify that get_methods returns the expected list. """

        self.assertEqual(['another_method', 'test'], self.actor.get_methods())

    def testHandler(self):
        """ Verify that the Actor is responding to proxied method calls. """

        self.pubsub.subscribe('proxy:noexist_actor')
        count = self.redis.publish('actor:noexist_actor',
                                   ('noexist_actor', 'test', (), {}))
        self.assertEqual(1, count)
        message = self.pubsub.get_message()  # pylint: disable=I0011,E1101
        self.assertEqual(message['channel'], 'proxy:noexist_actor')
        self.assertEqual(1, message['data'])
        self.pubsub.unsubscribe('proxy:noexist_actor')


if __name__ == '__main__':
    unittest.main()

""" Decorators unit tests for rodario framework """

# stdlib
import unittest

# local
from rodario.actors import Actor
from rodario.decorators import blocking
from rodario.registry import Registry


# pylint: disable=R0201
class TestActor(Actor):

    """ Stubbed Actor class for testing """

    @blocking
    def test(self):
        """ Simple method call. """

        return 1


# pylint: disable=C0103,R0904
class DecoratorsTests(unittest.TestCase):

    """ Decorators unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor and an ActorProxy for it. """

        cls.actor = TestActor(uuid='noexist_decorator')
        cls.actor.start()
        cls.proxy = cls.actor.proxy()
        cls.registry = Registry()

    @classmethod
    def tearDownClass(cls):
        """ Kill the actor. """

        cls.actor.stop()
        cls.registry.unregister('noexist_actor')  # pylint: disable=E1101

    def testBlockingMethod(self):
        """ Fire the @blocking method and make sure the result is valid. """

        self.assertEqual(1, self.proxy.test())

if __name__ == '__main__':
    unittest.main()

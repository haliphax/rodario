""" Registry unit tests for rodario framework """

# stdlib
import unittest

# local
from rodario.actors import Actor, ActorProxy
from rodario.registry import Registry
from rodario.exceptions import RegistrationException


class RegistryTestActor(Actor):

    """ Stubbed Actor class for testing """

    def __init__(self):
        """ Call super's __init__ so that we can access the UUID. """

        super(RegistryTestActor, self).__init__()


# pylint: disable=C0103,E1101
class RegistryTests(unittest.TestCase):

    """ Registry unit tests """

    @classmethod
    def setUpClass(cls):
        """ Grab the Registry singleton. """

        cls.registry = Registry()

    @classmethod
    def tearDownClass(cls):
        """ Be sure that our actors are not registered. """

        cls.registry.unregister('noexist_registry')

    def testUnregisterActor(self):
        """ Register and unregister a UUID. """

        self.registry.register('noexist_registry')
        self.registry.unregister('noexist_registry')

    def testRegisterTakenUUID(self):
        """ Try to register a UUID that has already been registered. """

        self.registry.register('noexist_registry')
        self.assertRaises(RegistrationException, self.registry.register,
                          'noexist_registry')
        self.registry.unregister('noexist_registry')

    def testDoesNotExist(self):
        """ Test that an invalid UUID does not exist in the registry. """

        self.assertFalse(self.registry.exists('noexist_registry'))

    def testExists(self):
        """ Test that a valid UUID does exist in the registry. """

        self.registry.register('noexist_registry')
        self.assertTrue(self.registry.exists('noexist_registry'))
        self.registry.unregister('noexist_registry')

    def testReturnsProxy(self):
        """ Test that a valid proxy is returned upon request. """

        actor = RegistryTestActor()
        actor.start()
        proxy = self.registry.get_proxy(actor.uuid)
        self.assertTrue(isinstance(proxy, ActorProxy))
        actor.stop()
        actor.__del__()

    def testListActors(self):
        """ Test that a valid list of actors is returned upon request. """

        self.registry.register('noexist_registry')
        self.assertSetEqual(self.registry.actors, set(('noexist_registry',)))
        self.registry.unregister('noexist_registry')

if __name__ == '__main__':
    unittest.main()

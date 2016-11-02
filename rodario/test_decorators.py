""" Decorators unit tests for rodario framework """

# stdlib
import unittest
from time import time, sleep

# local
from rodario.actors import Actor, ClusterProxy
from rodario.decorators import blocking, singular, DecoratedMethod
from rodario.registry import Registry

# 3rd party
import redis


def before_hook(func):
    """
    Before-hook method decorator for test purposes.

    :param instancemethod func: The function to wrap
    :rtype: :class:`rodario.decorators.DecoratedMethod`
    """

    # pylint: disable=W0613
    def before_func(self, *args, **kwargs):
        """ Return a different value. """

        return 2

    # if it's already a DecoratedMethod, just add to it
    if isinstance(func, DecoratedMethod):
        func.decorations.add('before_hook')
        func.after.append(before_func)

        return func

    # otherwise, instantiate a new one with our wrapper/bindings by default
    return DecoratedMethod(func, ('before_hook',), before=(before_func,))

def after_hook(func):
    """
    After-hook method decorator for test purposes.

    :param instancemethod func: The function to wrap
    :rtype: :class:`rodario.decorators.DecoratedMethod`
    """

    # pylint: disable=W0613
    def after_func(self, result, *args, **kwargs):
        """ Return a different value. """

        return 2

    # if it's already a DecoratedMethod, just add to it
    if isinstance(func, DecoratedMethod):
        func.decorations.add('after_hook')
        func.after.append(after_func)

        return func

    # otherwise, instantiate a new one with our wrapper/bindings by default
    return DecoratedMethod(func, ('after_hook',), after=(after_func,))


# pylint: disable=R0201
class TestActor(Actor):

    """ Stubbed Actor class for testing """

    @blocking
    def test(self):
        """ Simple method call. """

        return 1

    @singular
    def test_singular(self):
        """ Simple singular cluster method. """

        return 3

    @singular
    @blocking
    def test_both(self):
        """ More than one decoration. """

        return 1

    @blocking
    @singular
    def test_both_reverse(self):
        """ Reverse order of decoration list. """

        return 1

    @singular
    def test_expiry(self):
        """ Test the lock sanity check. """

        return 3

    @after_hook
    def test_after_hook(self):
        """ Test the after-hook binding. """

        return 1

    @before_hook
    def test_before_hook(self):
        """ Test the before-hook binding. """

        return 1


# pylint: disable=C0103,R0904
class DecoratorsTests(unittest.TestCase):

    """ Decorators unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor and an ActorProxy for it. """

        cls.actor = TestActor(uuid='noexist_decorator')
        cls.costar = TestActor(uuid='noexist_decorator2')
        cls.actor.start()
        cls.costar.start()
        cls.proxy = cls.actor.proxy()
        cls.registry = Registry()
        cls.cluster = ClusterProxy('decorators_test')
        cls._redis = redis.StrictRedis()

    @classmethod
    def tearDownClass(cls):
        """ Kill the actor. """

        cls.actor.stop()
        cls.registry.unregister('noexist_actor')  # pylint: disable=E1101

    def testDecorationCount(self):
        """ Test that the number of decorations is accurate. """

        self.assertEqual(2, len(self.actor.test_both.decorations))

    def testBlockingMethod(self):
        """ Fire the @blocking method and make sure the result is valid. """

        self.assertEqual(1, self.proxy.test())

    def testSingularMethod(self):
        """ Fire the @singular method and make sure there is a result. """

        sleep(1)
        self._redis.delete('global.lock:test_singular')
        self.actor.join('decorators_test')
        self.costar.join('decorators_test')
        future = self.cluster.test_singular()
        # first value is number of workers in cluster pool
        self.assertEqual(2, future.get())
        # second value is the actual function call result
        self.assertEqual(3, future.get(timeout=3))
        self._redis.delete('global.lock:test_singular')
        self.actor.part('decorators_test')
        self.costar.part('decorators_test')

    def testLockExpiry(self):
        """ Exercise the lock sanity check for singular methods. """

        # pylint: disable=W0101
        self._redis.set('global.lock:test_expiry', time() - 10)
        self.actor.join('decorators_test')
        self.costar.join('decorators_test')
        future = self.cluster.test_expiry()
        # first value is number of workers in cluster pool
        self.assertEqual(2, future.get())
        # second value is the actual function call result
        self.assertEqual(3, future.get(timeout=3))
        self.actor.part('decorators_test')
        self.costar.part('decorators_test')

    def testBeforeHook(self):
        """ Test the before-hook DecoratedMethod binding. """

        self.assertEqual(2, self.actor.test_before_hook())

    def testAfterHook(self):
        """ Test the after-hook DecoratedMethod binding. """

        self.assertEqual(2, self.actor.test_after_hook())

if __name__ == '__main__':
    unittest.main()

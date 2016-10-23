""" ClusterProxy unit tests for rodario framework """

# stdlib
import unittest
from time import sleep

# 3rd party
import redis

# local
from rodario.actors import Actor, ClusterProxy
from rodario.exceptions import EmptyClusterException
from rodario.future import Future

# pylint: disable=R0201


class TestActor(Actor):

    """ Stubbed Actor class for testing """

    def test(self):
        """ Simple method call. """

        return 1


# pylint: disable=C0103,R0904
class ClusterProxyTests(unittest.TestCase):

    """ ClusterProxy unit tests """

    @classmethod
    def setUpClass(cls):
        """ Create an Actor. """

        cls.actor = TestActor(uuid='cluster_test')
        cls.actor.start()
        cls.cluster = ClusterProxy('cluster_test')
        cls.redis = redis.StrictRedis()

    @classmethod
    def tearDownClass(cls):
        """ Kill the Actor. """

        cls.actor.stop()
        del cls.cluster._stop
        sleep(1)

    def testEmptyCluster(self):
        """ Throw an EmptyClusterException. """

        # pylint: disable=W0212
        self.assertRaises(EmptyClusterException, self.cluster._proxy, 'test')

    def testProxiedMethod(self):
        """ Call a proxied method. """

        self.actor.join('cluster_test')
        result = self.cluster.test()
        self.assertIsInstance(result, Future)
        self.assertEqual(1, result.get(timeout=1))
        self.actor.part('cluster_test')

    def testMessageHandler(self):
        """ Send a message. """

        self.actor.join('cluster_test')
        self.redis.publish('cluster_test', 'test')
        self.actor.part('cluster_test')

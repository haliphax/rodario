# stdlib
import inspect
import time

# 3rd party
from redis import StrictRedis

# local
import rodario
rodario.get_redis_connection = lambda: StrictRedis(host='localhost')
from rodario.actors import Actor, ActorProxy


class MyActor(Actor):

    def __init__(self, name, uuid=None):
        self.name = name
        super(MyActor, self).__init__(uuid)
        self.join('test', self.channel_func)

    def greeting(self, prefix='The Great'):
        print 'Hello! My name is {prefix} {name}'.format(prefix=prefix,
                                                         name=self.name)
        return 'return value for {prefix}'.format(prefix=prefix)

    def channel_func(self, message):
        print 'Cluster message received by %s' % self.name


class Orchestrator(Actor):

    _count = 0

    def publish(self, message):
        self._count = self._redis.publish('cluster:test', 1)
        print 'Cluster channel subscriber count: %d' % self._count


if __name__ == '__main__':
    actor = MyActor('Rodario', 'rodario')
    actor2 = MyActor('Lesser Actor')
    actor.start()
    actor2.start()
    actor.greeting('The Intelligent')
    proxy = ActorProxy(uuid=actor.uuid)
    return_value1 = proxy.greeting('The Elegant')
    return_value2 = proxy.greeting()
    print return_value2.get()
    print return_value1.get()
    orchestrator = Orchestrator()
    orchestrator.publish('Test')
    time.sleep(1)

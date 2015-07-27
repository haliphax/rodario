# stdlib
import inspect
import time

# local
from rodario.actors import Actor, ActorProxy


class MyActor(Actor):

    def __init__(self, name, uuid=None):
        self.name = name
        super(MyActor, self).__init__(uuid)

    def greeting(self, prefix='The Great'):
        print 'Hello! My name is {prefix} {name}'.format(prefix=prefix,
                                                         name=self.name)
        return 'return value'

if __name__ == '__main__':
    actor = MyActor('Rodario', 'rodario')
    actor.start()
    actor.greeting('The Intelligent')
    proxy = ActorProxy(uuid=actor.uuid)
    return_value = proxy.greeting('The Elegant')
    print return_value.get()

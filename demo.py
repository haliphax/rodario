# stdlib
import inspect
import time

# local
from rodario.actors import Actor, ActorProxy
from rodario.decorators import blocking


class MyActor(Actor):

    def __init__(self, name, uuid=None):
        self.name = name
        super(MyActor, self).__init__(uuid)

    def greeting(self, prefix='The Great'):
        print 'Hello! My name is {prefix} {name}'.format(prefix=prefix,
                                                         name=self.name)
        return 'return value for {prefix}'.format(prefix=prefix)

    @blocking
    def long_greeting(self, prefix='The Great'):
        print 'Hello...'
        time.sleep(3)
        print 'My name is {prefix} {name}'.format(prefix=prefix, name=self.name)

        return 'return value for {prefix} long greet'.format(prefix=prefix)

if __name__ == '__main__':
    actor = MyActor('Rodario', 'rodario')
    actor.start()
    actor.greeting('The Intelligent')
    proxy = ActorProxy(uuid=actor.uuid)
    return_value1 = proxy.greeting('The Elegant')
    print proxy.long_greeting('The Irresistible')
    return_value2 = proxy.greeting()
    print return_value2.get()
    print return_value1.get()

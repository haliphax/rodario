""" Function decorators for rodario framework """


# pylint: disable=R0903
class DecoratedMethod(object):

    """ Generic decorated method """

    def __init__(self, func, decorations=None, bindings=None):
        """
        Wrap the given function.

        :param instancemethod func: The function to wrap
        """

        self._func = func
        self._instance = None
        self.decorations = set(decorations) if decorations is not None else set()
        self.bindings = list(bindings) if bindings is not None else list()

    def __get__(self, obj, cls=None):
        """
        Return the callable and store a reference to the class instance.

        :param object obj: The instance object
        :param type cls: The type of the object
        :rtype: :class:`rodario.decorators.DecoratedMethod`
        """

        self._instance = obj

        return self

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function and map `self` to the stored instance.

        :rtype: mixed
        """

        result = None

        # call each of its bindings first
        for callee in self.bindings:
            result = callee(self._instance, *args, **kwargs)

            if result is not None:
                return result

        result = self._func(self._instance, *args, **kwargs)
        return result

def blocking(func):
    """
    Block the thread and return the proxied method call's result. This is
    sloppy and needs some work - the actual blocking is done within the Actor
    class after checking the method's decorations.

    :param instancemethod func: The function to wrap
    :rtype: :class:`rodario.decorators.DecoratedMethod`
    """

    # if it's already a DecoratedMethod, just add to it
    if isinstance(func, DecoratedMethod):
        func.decorations.add('blocking')
        return func

    # otherwise, instantiate a new one with our wrapper/bindings by default
    return DecoratedMethod(func, ('blocking',))

def singular(func):
    """
    First-come, first-served cluster channel call. Unlike the @blocking
    decorator, this is self-contained. All of the work happens right here.
    Needs some work - should accept parameters for context and expiry.

    :param instancemethod func: The function to wrap
    :rtype: :class:`rodario.decorators.DecoratedMethod`
    """

    from time import time

    expiry = 2
    context = None

    # pylint: disable=W0613,W0212
    def call_singular(self, *args, **kwargs):
        """
        Call the method if we can get a lock.

        :rtype: mixed
        :returns: The function result if a lock is acquired; otherwise, False.
        """

        current = time()
        lock_expires = current + expiry + 1
        lock_context = 'global.lock' if not context else context
        lock_name = '%s:%s' % (lock_context, func.__name__)

        # try to get lock; if we fail, do sanity check on lock
        if not self._redis.setnx(lock_name, lock_expires):
            # see if current lock is expired; if so, take it
            if current < float(self._redis.get(lock_name)):
                # lock is not expired
                return False
            elif current < float(self._redis.getset(lock_name, lock_expires)):
                # somebody else beat us to it
                return False

        # we have the lock; give it a TTL and pass through
        self._redis.expire(lock_name, expiry)

    # if it's already a DecoratedMethod, just add to it
    if isinstance(func, DecoratedMethod):
        func.decorations.add('singular')
        func.bindings.append(call_singular)
        return func

    # otherwise, instantiate a new one with our wrapper/bindings by default
    return DecoratedMethod(func, ('singular',), (call_singular,))

""" Function decorators for rodario framework """

# local
from rodario.util import acquire_lock

# pylint: disable=R0903,W0613


class DecoratedMethod(object):

    """ Generic decorated method """

    #: Set of decorator tags
    decorations = set()
    #: List of before-hook functions
    before = list()
    #: List of after-hook functions
    after = list()

    def __init__(self, func, decorations=None, before=None, after=None):
        """
        Wrap the given function.

        :param function func: The function to wrap
        :param set decorations: The decorator tags to attach
        :param list before: The list of before-hook functions
        :param list after: The list of after-hook functions
        """

        self._func = func
        self._instance = None
        self.decorations = set(
            decorations) if decorations is not None else set()
        self.before = list(before) if before is not None else list()
        self.after = list(after) if after is not None else list()

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

        # call each of its before-hook bindings first
        for callee in self.before:
            result = callee(self._instance, *args, **kwargs)

            if result is not None:
                return result

        result = self._func(self._instance, *args, **kwargs)

        # now call each of the after-hook bindings
        for callee in self.after:
            mutated = callee(self._instance, result, *args, **kwargs)

            if mutated is not None:
                return mutated

        return result

    @staticmethod
    def decorate(func, decorations=None, before=None, after=None):
        """
        Decorate the given function. If it is already a `DecoratedMethod`, it
        will be appended to rather than overwritten.

        :param set decorations: The decorator tags to attach
        :param list before: The list of before-hook functions
        :param list after: The list of after-hook functions
        :rtype: :class:`rodario.decorators.DecoratedMethod`
        :returns: A ``DecoratedMethod`` wrapper around ``func``
        """

        if isinstance(func, DecoratedMethod):
            if decorations is not None:
                func.decorations |= set(decorations)
            if before is not None:
                func.before += list(before)
            if after is not None:
                func.after += list(after)
        else:
            func = DecoratedMethod(func, decorations, before, after)

        return func


def singular(func):
    """
    First-come, first-served cluster channel call. Needs some work; should
    accept parameters for context and expiry.

    :param function func: The function to wrap
    :rtype: :class:`rodario.decorators.DecoratedMethod`
    """

    context = None

    def before_singular(self, *args, **kwargs):
        """
        Call the method if we can get a lock.

        :rtype: mixed
        :returns: None if a lock is acquired; otherwise, False.
        """

        # pylint: disable=W0212
        if not acquire_lock(func.__name__, conn=self._redis):
            return False

    def after_singular(self, result, *args, **kwargs):
        """
        Clean up the lock.
        """

        lock_context = 'global.lock' if not context else context
        lock_name = '%s:%s' % (lock_context, func.__name__)
        self._redis.delete(lock_name)  # pylint: disable=W0212

    return DecoratedMethod.decorate(func, ('singular',), (before_singular,),
                                    (after_singular,))

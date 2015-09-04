""" Function decorators for rodario framework """


# pylint: disable=R0903
class BlockingMethod(object):

    """ Blocking proxy method """

    def __init__(self, func):
        """
        Wrap the given function.

        :param instancemethod func: The function to wrap
        """

        self._func = func
        self._instance = None

    def __get__(self, obj, cls=None):
        """
        Return the callable and store a reference to the class instance.

        :param object obj: The instance object
        :param type cls: The type of the object
        :rtype: :class:`rodario.decorators.BlockingMethod`
        """

        self._instance = obj

        return self

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function and map `self` to the stored instance.

        :rtype: mixed
        """

        return self._func(self._instance, *args, **kwargs)


def blocking(func):
    """
    Block the thread and return the proxied method call's result.

    :param instancemethod func: The function to wrap
    :rtype: :class:`rodario.decorators.BlockingMethod`
    """

    return BlockingMethod(func)

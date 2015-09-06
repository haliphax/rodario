""" Future response type for rodario framework """


class Future(object):

    """ Custom response type for proxied method calls """

    def __init__(self, queue):
        """
        Initialize the Future by saving a reference to the Queue

        :param multiprocessing.Queue queue: The response queue to wrap
        """

        self._queue = queue

    @property
    def ready(self):
        """
        Return True if the response value is available.

        :rtype: :class:`bool`
        """

        return not self._queue.empty()

    def get(self, *args, **kwargs):
        """
        Resolve and return the proxied method call's value.

        :rtype: mixed
        """

        return self._queue.get(*args, **kwargs)

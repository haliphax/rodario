rodario
=======

A simple, redis-backed Python actor framework

* `Homepage <https://github.com/haliphax/rodario>`_

.. toctree::
    :maxdepth: 2

Connection
----------

By default, rodario will use a ``StrictRedis`` connection to localhost on the
default port. If you wish to override this behavior, then replace the
``rodario.get_redis_connection`` method after import::

    from redis import StrictRedis
    import rodario
    rodario.get_redis_connection = lambda: StrictRedis(host='1.2.3.4')

The Registry
------------

.. autoclass:: rodario.registry.Registry
    :members:

    .. automethod:: rodario.registry.Registry.__new__

.. autoclass:: rodario.registry._RegistrySingleton
    :members:

    .. automethod:: rodario.registry._RegistrySingleton.__init__

Actors and Proxies
------------------

.. autoclass:: rodario.actors.Actor
    :members:

    .. automethod:: rodario.actors.Actor.__init__

.. autoclass:: rodario.actors.ActorProxy
    :members:

    .. automethod:: rodario.actors.ActorProxy.__init__
    .. automethod:: rodario.actors.ActorProxy._proxy

.. autoclass:: rodario.actors.ClusterProxy
    :members:

    .. automethod:: rodario.actors.ClusterProxy.__init__
    .. automethod:: rodario.actors.ClusterProxy._proxy

.. autoclass:: rodario.future.Future
    :members:

    .. automethod:: rodario.future.Future.__init__

Decorators
----------

.. autoclass:: rodario.decorators.DecoratedMethod
    :members:

    .. automethod:: rodario.decorators.DecoratedMethod.__init__

.. autofunction:: rodario.decorators.singular

Exceptions
----------

.. autoclass:: rodario.exceptions.InvalidActorException
.. autoclass:: rodario.exceptions.InvalidProxyException
.. autoclass:: rodario.exceptions.UUIDInUseException
.. autoclass:: rodario.exceptions.RegistrationException
.. autoclass:: rodario.exceptions.EmptyClusterException

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


rodario
=======

A simple, redis-backed Python actor framework

* `Homepage <https://github.com/haliphax/rodario>`_

.. toctree::
    :maxdepth: 2

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

.. autoclass:: rodario.future.Future
    :members:

    .. automethod:: rodario.future.Future.__init__

Decorators
----------

.. autofunction:: rodario.decorators.blocking

Exceptions
----------

.. autoclass:: rodario.exceptions.InvalidActorException
.. autoclass:: rodario.exceptions.InvalidProxyException
.. autoclass:: rodario.exceptions.UUIDInUseException
.. autoclass:: rodario.exceptions.RegistrationException

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


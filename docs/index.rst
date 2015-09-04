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
    :undoc-members:

    .. automethod:: rodario.registry.Registry.__new__

.. autoclass:: rodario.registry._Singleton
    :members:
    :undoc-members:

    .. automethod:: rodario.registry._Singleton.__init__

Actors and Proxies
------------------

.. autoclass:: rodario.actors.Actor
    :members:
    :undoc-members:

    .. automethod:: rodario.actors.Actor.__init__

.. autoclass:: rodario.actors.ActorProxy
    :members:
    :undoc-members:

    .. automethod:: rodario.actors.ActorProxy.__init__
    .. automethod:: rodario.actors.ActorProxy._proxy

Decorators
----------

.. autofunction:: rodario.decorators.blocking

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


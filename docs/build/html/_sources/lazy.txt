Lazy evaluation (``bottle_utils.lazy``)
=======================================

This module provides classes and decorators for lazy evaluation of callables.

The basic idea is that a decorated callable returns a proxy object instead of
evaluating the callable immediately. This proxy object will then evaluate the
callable when the value is actually used (e.g., adding to it, subtracting from
it, coercing, calling, accessing attributes, and so on).

Implementation is not perfect and some properties of the callable's return
values are not perfectly mimiced by the proxy object. This has some weird
side-effects like not being able to interpolate what is otherwise supposed to
be a string return value. For most part, though, it works.

Functions and classes
---------------------

.. automodule:: bottle_utils.lazy
   :members:


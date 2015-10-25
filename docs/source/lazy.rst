Lazy evaluation (``bottle_utils.lazy``)
=======================================

This module provides classes and decorators for lazy evaluation of callables.

Lazily evaluated functions and methods return immediately without performing
any work, and their work is performed at some later point in time when the
results are actually needed. This is useful in situation when the result may or
may not be needed (e.g., some branching may occur) or when evaluation of the
result may not be possible at the time of a call but we know it will be
possible later.

In Bottle Utils, lazy evaluation is used extensively in the
:py:mod:`~bottle_utils.i18n` module. Because evaluating the translation context
requires a request context, and it may not be available where the call happens,
lazy evaluation postpones evaluation of the translation function until we are
sure the request context exists (e.g., some translated string is stored as a
defined constant somewhere and used later in the request handler).

How it works
------------

When a function is wrapped in a :py:class:`~Lazy` object, it behaves like
result of evaluating that function. It stores the function in one of its
properties and waits for your code to actually try to use the result. If your
code never uses the result, the wrapped function is never called. When your
code uses the result, the function is then evaluated for the first time. This
type of object is sometimes also referred to as a proxy.

The idea of 'using' the result is defined as an attempt to coerce or perform
any action that triggers any of the `magic methods
<https://docs.python.org/3/reference/datamodel.html>`_. This includes things
like adding or subtracting from another value, calling ``str()``, ``bool()``
and similar methods, attempting string interpolation with either ``format()``
method or ``%`` operator, accessing indices or keys using subscript notation, 
and so on. Attempting to access methods and properties also counts as 'using'.

One caveat of this behavior is that, because lazy functions are created in one
context and potentially evaluated in another, the state in which they are
evaluated may change in unpredictable ways. On the other hand, this may create
opportunities that would not exist without lazy evaluation.

More on lazy evaluation in general can be found `in Content Creation Wiki
<http://c2.com/cgi/wiki?LazyEvaluation>`_.

Module contents
---------------

.. automodule:: bottle_utils.lazy
   :members:


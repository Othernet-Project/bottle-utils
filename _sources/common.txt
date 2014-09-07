Common utilities (``bottle_utils.common``)
==========================================

The ``bottle_utils.common`` module contains functions and constants that are
used in other modules.

This module also contains a few constants and variables that improve code that
targets both Python 2.x and Python 3.x. Note, though, that this mostly works in
the context of Bottle Utils and hasn't been tested in too many different
versions of Python. If you want a more comprehensive solution, you should look
at six_.

``bottle_utils.common.PY2`` is a constant that is set to ``True`` if Python
version is 2.x. Conversely, ``bottle_utils.common.PY3`` is used to detect if
Python version is 3.x.

This module also contains names ``unicode`` and ``basestring``, which work as
expected in both Python 2.x and Python 3.x.

Functions
---------

.. automodule:: bottle_utils.common
   :members:
   :exclude-members: unicode, basestring


.. _six: https://pypi.python.org/pypi/six

Social metadata (``bottle_utils.meta``)
=======================================

This module provides classes for working with social meta data (Facebook,
Google+, Twitter).

How it works
------------

There are two flavors of meta data classes,
:py:class:`~bottle_utils.meta.SimpleMetadata` and
:py:class:`~bottle_utils.meta.Metadata`. Both render the title tag and
description met tag, while the latter also renders a full set of social meta
tags used by Facebook, Google+, and Twitter.

Using any of the two classes, you normally instantiate an object passing it
meta data as constructor arguments, and then simply use the objects as string
values in the template. You can also call the ``render()`` method on the
object, but that is redundant except in rare cases where ``str`` type is
expected.

Example usage is provided for both of the classes.

Classes
-------

.. automodule:: bottle_utils.meta
   :members:
   :show-inheritance:


Social metadata (``bottle_utils.meta``)
=======================================

This module provides classes for working with social metadata (Facebook,
Google+, Twitter).

How it works
------------

There are two flavors of metadata classes,
:py:class:`~bottle_utils.meta.SimpleMetadata` and
:py:class:`~bottle_utils.meta.Metadata`. Both render the title tag and
description met tag, while the latter also renders a full set of social meta
tags used by Facebook, Google+, and Twitter.

Using any of the two classes, you normally instantiate an object passing it
metadata as constructor arguments, and then simply use the objects as string
values in the template. You can also call the ``render()`` method on the
object, but that is redundant except in rare cases where ``str`` type is
expected.

Example usage is provided for both of the classes.

.. warning::
    Authors of this module use social metadata only very rarely. As such, the
    features found in this module may not always be up to date. Please file
    issues you find with the social metadata support to the `GitHub issue
    tracker <https://github.com/Outernet-Project/bottle-utils/issues/>`_.

Classes
-------

.. automodule:: bottle_utils.meta
   :members:


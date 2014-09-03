============
Bottle utils
============

Assortment of frequently used utilities for Bottle.

This package contains utilities for developing web sites and web applications
using Bottle_ framework. It is divided into 5 modules of
which the ``lazy`` module is not Bottle-specific.

The bottle-utils are created from a bunch of unrelated modules we frequently
used at Outernet_. Some of the modules have been tested fairly thoroughly, and
some have been used only in a handful of projects. Therefore, not all modules
are of high quality. You should conisder this package Alpha quality.

Status
======



Modules
=======

The following modules are currently available:

- ``bottle_utils.ajax`` - Decorators for AJAX-specific handlers
- ``bottle_utils.csrf`` - Decorators for CSRF protection
- ``bottle_utils.http`` - Decorators for managing HTTP reponse headers
- ``bottle_utils.i18n`` - Support for internationalization
- ``bottle_utils.lazy`` - Provides functionality for lazy evaluation of 
  callables

Documentation is currently not available.

Bugs
====

Please report all bugs to our `GitHub issue tracker`_.

License
=======

This package is licensed under BSD license. See LICENSE_ for more
info.

.. _Bottle: http://bottlepy.org/
.. _Outernet: https://www.outernet.is/
.. _GitHub issue tracker: https://github.com/Outernet-Project/bottle-utils/issues
.. _LICENSE: LICENSE

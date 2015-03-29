.. Bottle Utils documentation master file, created by
   sphinx-quickstart on Sun Sep 07 11:37:09 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bottle Utils documentation
==========================

Bottle Utils (package name ``bottle-utils``) is a collection of decorators,
functions and classes that address typical problems developing web sites and
applications using `Bottle framework`_. This package is created based on code
we use at Outernet_ for various user-facing interfaces as well as our own
sites.

Bottle Utils are compatible with Python 2.7, 3.3, and 3.4. Compatibility with
other versions of Python is possible, but not tested. It targets latest stable 
release of Bottle.

Installation
============

The ``bottle-utils`` package is a virtual package that bundles togehter several
related packages that, together, comprise Bottle Utils. You can install all
related packages by installing this package::

    pip install bottle-utils

    easy_install bottle-utils

You can also install individual packages. Here is a list of all packages that
are part of Bottle Utils:

- ``bottle-utils-common`` - Common functionalities shared by other packages
- ``bottle-utils-ajax`` - Decorators for AJAX-specific handlers
- ``bottle-utils-csrf`` - Decorators for CSRF protection
- ``bottle-utils-flash`` - Plugin and methods for flash messaging
- ``bottle-utils-html`` - Functions for use in HTML templates
- ``bottle-utils-http`` - Decorators for managing HTTP reponse headers
- ``bottle-utils-i18n`` - Support for internationalization
- ``bottle-utils-lazy`` - Provides functionality for lazy evaluation of 
  callables
- ``bottle-utils-meta`` - Classes for handling page/social metadata

Source code
===========

The complete source code is licensed under BSD license (see ``LICENSE`` file in
the source package), and available `on GitHub`_.

Package contents
================

The following functionality is available:

.. toctree::
   :maxdepth: 1

   common
   ajax
   csrf
   flash
   html
   http
   i18n
   lazy
   meta
   ...

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Bottle framework: http://bottlepy.org/
.. _Outernet: https://www.outernet.is/
.. _on GitHub: https://github.com/Outernet-Project/bottle-utils

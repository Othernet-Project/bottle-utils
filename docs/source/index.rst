.. Bottle Utils documentation master file, created by
   sphinx-quickstart on Sun Sep 07 11:37:09 2014.

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

Use one of the following commands to install Bottle Utils::

    pip install bottle-utils

    easy_install bottle-utils

.. note::
    Between versions 0.3 and 0.5, bottle-utils package was split into multiple
    packages. Packages were structured in a way that allowed the API prior to
    version 0.3 to work without issues. However, this has caused various
    problems with deployment and development, and the approach was subsequently
    abandoned. Starting with version 0.5, Bottle Utils is again a monolithic
    package.

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
   forms
   http
   i18n
   lazy
   meta

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Bottle framework: http://bottlepy.org/
.. _Outernet: https://www.outernet.is/
.. _on GitHub: https://github.com/Outernet-Project/bottle-utils

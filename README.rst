============
Bottle utils
============

Assortment of frequently used utilities for Bottle.

This package contains utilities for developing web sites and web applications
using Bottle_ framework. It is divided into several modules of
which the ``lazy`` module is not Bottle-specific.

The bottle-utils are created from a bunch of unrelated modules we frequently
used at Outernet_. Some of the modules have been tested fairly thoroughly, and
some have been used only in a handful of projects. Therefore, not all modules
are of high quality. You should conisder this package Alpha quality.

Between versions 0.3 and 0.4.dev1, bottle-utils have been split into multiple
packages. Since 0.4.dev1, they have been remerged into a single packages as we
normally use them together, and having them as separate packages causes various
deployment issues.

Installation
============

Install using ``pip`` or ``easy_install``::

    pip install bottle-utils

    easy_install bottle-utils

Documentation
=============

Detailed documentation is available online_.

You can also generate offline documentation by cloning this repository and
doing the following::

    cd /path/to/repo
    cd docs
    make html

The ``docs/build/html`` directory should contain full HTML documentation. You
can start from the ``index.html`` file.

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
.. _online: http://outernet-project.github.io/bottle-utils/


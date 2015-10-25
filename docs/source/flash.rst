Flash messages (``bottle_utils.flash``)
=======================================

Flash messages are messages that are generated in one handler and displayed to
the user in another. Commonly, this is done when you want to redirect to
another path and still show the results of an operation performed in another.
One example would be "You have logged out" message after logging the user out.

There are several ways to do this, but storing the message in a cookie is the
most straightforward. This module provides methods for doing just that.

Unicode strings are fully supported.

Basic usage
-----------

In order to make flash messaging available to your app, install the
:py:func:`~bottle_utils.flash.message_plugin` plugin. ::

    bottle.install(message_plugin)

This makes ``bottle.request.message`` object and ``bottle.response.flash()``
method available to all request handlers. To set a message, use
``response.flash()``::

    response.flash('This is my message')

To show the message in the interface, make the ``request.message`` object
available to your template's context and simply output it in your template::

    <p class="flash">{{ message }}</p>

How it works
------------

When a message is set, it is stored in a cookie in the user's browser. The
``bottle.request.message`` is a lazy object (see
:py:class:`~bottle_utils.lazy.Lazy`), and **does not do anything until you
actually use the message**. When you access the message object, it retrieves
the text from the cookie and clears the cookie.

.. warning::

   There is no mechanism for automatically clearing messages if they are not
   consumed. Therefore, it is important to consume it at the very next step
   user takes in your app. Otherwise, the message may appear on an unpexpected
   page at unexpected time, taken out of context, and confuse the user.

Functions and plugins
---------------------

.. automodule:: bottle_utils.flash
   :members:
   :exclude-members: get_message

   .. autofunction:: get_message()

Flash messages (``bottle_utils.flash``)
=======================================

Flash messages are messages that are generated in one handler and displayed to
the user in another. Commonly, this is done when you want to redirect to
another path and still show the results of an operation performed in another.
One example would be "You have logged out" message after logging the user out.

Unicode strings are fully supported.

There are several ways to do this, but storing the message in a cookie is the
most straightforward. This module provides methods for doing just that.

How it works
------------

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

When a message is set, it is stored in a cookie in the user's browser. When you
use the message object, the value of the cookie is output, and the cookie is
removed.

.. note::

   There is no mechanism of automatically clearign messages if they are not
   consumed. Therefore, it is important to consume it at the very next step
   user takes in your app. If your handler redirects to a few different paths
   depending on the results of processing user requests, all target handlers
   should be set to consume the message or the message may appear on an
   unpexpected page at unexpected time, taken out of context, and confuse the
   user.

Functions and plugins
---------------------

.. automodule:: bottle_utils.flash
   :members:
   :exclude-members: get_message

   .. autofunction:: get_message()

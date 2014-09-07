CSRF protection (``bottle_utils.csrf``)
=======================================

This module contains decorators and functions for facilitating CSRF_
protection.

App configuration
-----------------

Functions in this module require the Bottle application to be configured_ with
CSRF-specific options.

Here is an example of file-based configuration::

    [csrf]
    secret = SomeSecretValue
    token_name = _csrf_token
    path = /
    expires = 600

``secret`` setting is the only setting you really must override. Not having
this setting set will result in ``KeyError`` exception.

When using dict-based configuration, prefix each key with ``csrf.``.

The keys have following meaning:

- ``secret`` setting is a secret key used for setting cookies; it should be
  fairly random and difficult to guess
- ``token_name`` setting is the name of the cookie and form field that contain
  the token
- ``path`` setting is the path of the cookie
- ``expires`` setting is in seconds and sets the cookie's max-age


Caveat
------

As with most common CSRF protection schemes, decorators in this module will
prevent the user from opening two forms and submitting them one after the
other. This also applies to cases where forms are fetched from server side
using XHR.

Every form must have a token, and a token must match the one in the cookie.
However, there is only one cookie for the whole site. When you submit a form,
the token in the cookie is replaced with a new one, making tokens in any of the
previously opened forms invalid. The result is that form submission results in
a HTTP 403 response (not authorized).

You need to decide whether you can live with this behavior before using this
module. In case of XHR, consolidating different forms into a single form or
fetching tokens separately may be viable solutions.

Functions and decorators
------------------------

.. automodule:: bottle_utils.csrf
   :members:
   :exclude-members: get_conf

.. _CSRF:: http://en.wikipedia.org/wiki/Cross-site_request_forgery
.. _configured: http://bottlepy.org/docs/0.12/configuration.html

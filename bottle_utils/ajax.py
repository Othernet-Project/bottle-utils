"""
.. module:: bottle_utils.ajax
   :synopsis: Utility functions for handling ajax

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import functools

from bottle import request, abort


def ajax_only(func):
    """
    This decorator simply tests if request ``is_xhr`` and aborts any requests
    that are not XHR with an HTTP 400 status code. Keep in mind, though, that
    AJAX header ('X-Requested-With') can be faked, so don't use this decorator
    as a security measure of any kind.

    Example::

        @ajax_only
        def hidden_from_non_xhr():
            return "Foo!"

    :param func:    request handler
    :raises:        ``bottle.HTTPResponse``
    :returns:       wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_xhr:
            abort(400)
        return func(*args, **kwargs)
    return wrapper


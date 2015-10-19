"""
.. module:: bottle_utils.ajax
   :synopsis: Utility functions for handling ajax

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import functools

from bottle import request, abort, template, DictMixin, response


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


def roca_view(full, partial, **defaults):
    """
    Render partal for XHR requests and full template otherwise
    """
    templ = defaults.pop('template_func', template)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.is_xhr:
                tpl_name = partial

                # This is a workaround for Chrome's unexpected behavior when
                # using HTML5 push-state and browser's back button, where a
                # partial is loaded as sole content of the page without any
                # of the elements that were not returned as part of the
                # response to the AJAX request.
                # (see http://stackoverflow.com/a/11393281)
                response.headers['Cache-Control'] = 'no-store'
            else:
                tpl_name = full
            result = func(*args, **kwargs)
            if isinstance(result, (dict, DictMixin)):
                tplvars = defaults.copy()
                tplvars.update(result)
                return templ(tpl_name, **tplvars)
            elif result is None:
                return templ(tpl_name, defaults)
            return result
        return wrapper
    return decorator

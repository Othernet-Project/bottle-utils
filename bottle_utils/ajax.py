from __future__ import unicode_literals

import functools

from bottle import request, abort, template, DictMixin, response

from bottle_utils.common import to_bytes


def ajax_only(func):
    """
    Return HTTP 400 response for all non-XHR requests.

    .. warning::
        AJAX header ('X-Requested-With') can be faked, so don't use this
        decorator as a security measure of any kind.

    Example::

        @ajax_only
        def hidden_from_non_xhr():
            return "Foo!"

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_xhr:
            abort(400)
        return func(*args, **kwargs)
    return wrapper


def roca_view(full, partial, **defaults):
    """
    Render ``partal`` for XHR requests and ``full`` template otherwise. If
    ``template_func`` keyword argument is found, it is assumed to be a function
    that renders the template, and is used instead of the default one, which is
    ``bottle.template()``.

    .. note::
        To work around issues with Chrome browser (all platforms) when using
        this decorator in conjunction with HTML5 pushState, the decorator
        always adds a ``Cache-Control: no-store`` header to partial responses.

    Example::

        @roca_view('page.html', 'fragment.html')
        def my_roca_handler():
            return dict()

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
                response.headers[str('Cache-Control')] = str('no-store')
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

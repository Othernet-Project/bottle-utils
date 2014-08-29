"""
ajax.py: Utility functions for handling ajax

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import functools

from bottle import request, abort


def ajax_only(error_status=400):
    """ Aborts a request that is not made using AJAX """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_xhr:
                abort(error_status)
            return func(*args, **kwargs)
        return wrapper
    return decorator


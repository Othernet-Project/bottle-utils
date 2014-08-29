"""
http.py: Utility functions for HTTP (headers and similar)

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import functools

from bottle import response


def no_cache(func):
    """ Decorator: disables caching on handler """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        response.headers[b'Cache-Control'] = b'private, no-cache'
        return resp
    return wrapper

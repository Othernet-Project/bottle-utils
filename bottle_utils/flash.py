"""
flash.py: Cookie-based session messages

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import sys
import functools

from bottle import request, response

from .lazy import lazy


PY2 = sys.version_info.major == 2
MESSAGE_KEY = str('_flash')
ROOT = b'/'

# This is not to keep cookie content secret, it's to allow UTF8 cookies
SECRET = 'flash'


@lazy
def get_message():
    response.delete_cookie(MESSAGE_KEY, path=ROOT, secret=SECRET)
    return request._message


def set_message(msg):
    if PY2:
        msg = msg.encode('utf8')
    response.set_cookie(MESSAGE_KEY, msg, path=ROOT, secret=SECRET)
    request._message = msg


def message_plugin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cookie = request.get_cookie(MESSAGE_KEY, str(), secret=SECRET)
        if PY2:
            request._message = cookie.decode('utf8')
        else:
            request._message = cookie
        request.message = get_message()
        response.flash = set_message
        return func(*args, **kwargs)
    return wrapper


"""
csrf.py: Utility functions CSRF protection

Application configuration options:

    [csrf]
    secret =
    token_name = _csrf_token
    path = /
    expires = 600

The ``secret`` setting is the only setting you really must override. Not having
this setting set will result in ``KeyError`` exception. It is the secret value
that is used to

The ``token_name`` setting is the name of the cookie and form field that
contain the token.

The ``path`` setting is the path of the cookie.

The ``expires`` setting is in seconds and sets the cookie's max-age.

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import os
import hashlib

from bottle import request, response, abort


ROOT = b'/'
CSRF_TOKEN = b'_csrf_token'
EXPIRES = 600  # seconds
ENCODING = 'latin1'


def get_conf():
    conf = request.app.config
    csrf_secret = conf['csrf.secret']
    csrf_token_name = conf.get('csrf.token_name', CSRF_TOKEN).encode(ENCODING)
    csrf_path = conf.get('csrf.path', ROOT).encode(ENCODING)
    try:
        cookie_expires = int(conf.get('csrf.expires', EXPIRES))
    except ValueError:
        cookie_expires = EXPIRES
    return csrf_secret, csrf_token_name, csrf_path, cookie_expires


def generate_csrf_token():
    """ Generate and set new CSRF token in cookie

    The generated token is set to ``request.csrf_token`` attribute for easier
    access by other functions.
    """
    secret, token_name, path, expires = get_conf()
    sha256 = hashlib.sha256()
    sha256.update(os.urandom(8))
    token = sha256.hexdigest().encode(ENCODING)
    response.set_cookie(token_name, token, path=path,
                        secret=secret, max_age=expires)
    request.csrf_token = token


def csrf_token(func):
    """ CSRF token management

    The POST handler must use the ``csrf_protect`` decotrator for the token to
    be used in any way.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        secret, token_name, path, expires = get_conf()
        token = request.get_cookie(token_name, secret=secret)
        if token:
            # We will reuse existing tokens
            request.csrf_token = token.decode('utf8')
        else:
            generate_csrf_token()
        # Pages with CSRF tokens should not be cached
        response.headers['Cache-Control'] = 'private no-cache'
        return func(*args, **kwargs)
    return wrapper


def csrf_protect(func):
    """ CSRF protection

    Performs checks for CSRF protection. It is assumed that the GET request
    handler used the ``csrf_token`` middleware to supply the user with
    appropriate cookies and form data.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        secret, token_name, path, expires = get_conf()
        token = request.get_cookie(token_name, secret=secret)
        if not token:
            abort(403, 'The form you submitted is invalid or has expired')
        token = token.decode(ENCODING)
        form_token = request.forms.getunicode('_csrf_token')
        if form_token != token:
            response.delete_cookie(token_name, path=path, secret=secret,
                                   max_age=expires)
            abort(403, 'The form you submitted is invalid or has expired')
        generate_csrf_token()
        return func(*args, **kwargs)
    return wrapper


def csrf_tag(token=None):
    token = token or request.csrf_token
    return '<input type="hidden" name="_csrf_token" value="%s">' % token


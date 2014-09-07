"""
common.py: Common utility functions

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import sys
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from bottle import request, html_escape

__all__ = ('PY3', 'PY2', 'unicode', 'basestring', 'to_unicode', 'to_bytes',
           'attr_escape', 'html_escape', 'full_url', 'urlquote')

ESCAPE_MAPPING = (
    ('&', '&amp;'),
    ('"', '&quot;'),
    ('\n', '&#10;'),
    ('\r', '&#13;'),
    ('\t', '&#9;'),
)
PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3


if PY3:
    basestring = str
    unicode = str
if PY2:
    unicode = unicode
    basestring = basestring


def to_unicode(v, encoding=None):
    try:
        if encoding:
            return v.decode(encoding)
        return v.decode()
    except AttributeError:
        return unicode(v)


def to_bytes(v, encoding='utf8'):
    if isinstance(v, bytes):
        return v
    return v.encode(encoding, errors='ignore')


def attr_escape(attr):
    for s, r in ESCAPE_MAPPING:
        attr = attr.replace(s, r)
    return attr


def full_url(path='/'):
    parts = request.urlparts
    url = parts.scheme + '://' + parts.hostname
    if parts.port:
        url += ':' + str(parts.port)
    return url + path


def urlquote(s):
    s = to_bytes(s)
    return quote(s)

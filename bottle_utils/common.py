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

HTML_ESCAPE_MAPPING = ESCAPE_MAPPING + (
    ('<', '&lt;'),
    ('>', '&gt;'),
)

#: Whether Python version is 2.x
PY2 = sys.version_info.major == 2

#: Whether Python version is 3.x
PY3 = sys.version_info.major == 3


if PY3:
    basestring = str
    unicode = str
if PY2:
    unicode = unicode
    basestring = basestring


def to_unicode(v, encoding='utf8'):
    """
    Convert a value to Unicode string (or just string in Py3). This function
    can be used to ensure string is a unicode string. This may be useful when
    input can be of different types (but meant to be used when input can be
    either bytestring or Unicode string), and desired output is always Unicode
    string.

    The ``encoding`` argument is used to specify the encoding for bytestrings.
    """
    if isinstance(v, unicode):
        return v
    try:
        return v.decode(encoding)
    except (AttributeError, UnicodeEncodeError):
        return unicode(v)


def to_bytes(v, encoding='utf8'):
    """
    Convert a value to bytestring (or just string in Py2). This function is
    useful when desired output is always a bytestring, and input can be any
    type (although it is intended to be used with strings and bytestrings).

    The ``encoding`` argument is used to specify the encoding of the resulting
    bytestring.
    """
    if isinstance(v, bytes):
        return v
    try:
        return v.encode(encoding, errors='ignore')
    except AttributeError:
        return unicode(v).encode(encoding)


def attr_escape(attr):
    """
    Escape ``attr`` string containing HTML attribute value. This function
    escapes certain characters that are undesirable in HTML attribute values.
    Functions that construct attribute values using user-supplied data should
    escape the values using this function.
    """
    for s, r in ESCAPE_MAPPING:
        attr = attr.replace(s, r)
    return attr


def html_escape(html):
    """
    Escape ``html`` strning containing HTML. This function escapes characters
    that are not desirable in HTML markup, when the source string should
    represent text content only. User-supplied data that should appar in markup
    should be escaped using this function.
    """
    for s, r in HTML_ESCAPE_MAPPING:
        html = html.replace(s, r)
    return html


def full_url(path='/'):
    """
    Convert a specified path to full URL based on request data. This function
    uses the current request context information about the request URL to
    construct a full URL using specified path. In particular it uses
    ``bottle.request.urlparts`` to obtain information about scheme, hostname,
    and port (if any).

    Because it uses the request context, it cannot be called outside a request.
    """
    parts = request.urlparts
    url = parts.scheme + '://' + parts.hostname
    if parts.port:
        url += ':' + str(parts.port)
    return url + path


def urlquote(s):
    """
    Quote (URL-encode) a string with Unicode support. This is a simple wrapper
    for ``urllib.quote`` (or ``urllib.parse.quote``) that converts the input to
    UTF-8-encoded bytestring before quoting.
    """
    s = to_bytes(s)
    return quote(s)

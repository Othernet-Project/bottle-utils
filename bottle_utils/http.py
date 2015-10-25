"""
.. module:: bottle_utils.http
   :synopsis: HTTP decorators

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import os
import time
import functools

from bottle import (HTTPResponse, HTTPError, parse_date, parse_range_header,
                    request, response)

MIME_TYPES = {
    # Text/Code
    'txt': 'text/plain',
    'html': 'text/html',
    'css': 'text/css',
    'js': 'text/javascript',

    # Image
    'gif': 'image/gif',
    'jpg': 'image/jpeg',
    'tiff': 'image/tiff',
    'png': 'image/png',
    'svg': 'image/svg+xml',

    # Data/Document
    'pdf': 'application/pdf',
    'xml': 'text/xml',
    'json': 'application/json',

    # Video
    'mp4': 'video/mp4',
    'm4v': 'video/mp4',
    'ogv': 'video/ogg',
    'flv': 'video/x-flv',
    'webm': 'video/webm',
    '3gp': 'video/3gpp',
    'mpeg': 'video/mpeg',
    'mpg': 'video/mpeg',

    # Audio
    'mp3': 'audio/mpeg',
    'ogg': 'audio/ogg',
    'flac': 'audio/flac',
    'm4a': 'audio/mp4',
    'mpg': 'video/mpeg',

    # Other
    'zip': 'application/zip',
    'gz': 'application/gzip',
}
EXTENSIONS = list(MIME_TYPES.keys())
DEFAULT_TYPE = MIME_TYPES['txt']
TIMESTAMP_FMT = '%a, %d %b %Y %H:%M:%S GMT'


def no_cache(func):
    """
    Disable caching on a handler. The decorated handler will have
    ``Cache-Control`` header set to ``private, no-cache``.

    This is useful for responses that contain data that cannot be reused.

    Simply deocrate a handler with it::

        @app.get('/foo')
        @no_cache
        def not_cached():
            return 'sensitive data'
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        response.headers[b'Cache-Control'] = b'private, no-cache'
        return resp
    return wrapper


def get_mimetype(filename):
    """
    Guess mime-type based on file's extension.
    """
    name, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext[1:], DEFAULT_TYPE)


def format_ts(seconds=None):
    """
    Given a timestamp in seconds since UNIX epoch, return a string
    representation suitable for use in HTTP headers according to RFC.

    If ``seconds`` is omitted, the time is asumed to be current time.
    """
    return time.strftime(TIMESTAMP_FMT, time.gmtime(seconds))


def iter_read_range(fd, offset, length, chunksize=1024*1024):
    """
    Return an iterator that allows reading files in chunks. The ``fd`` should
    be a file-like object that has a ``read()`` method. The ``offset`` value
    sets the start offset of the read. If the ``fd`` object does not support
    ``seek()``, the file will be simply read up until offset, and the read data
    discarded.

    ``length`` argument specifies the amount of data to read. The read is not
    done in one go, but in chunks. The size of a chunk is specified using
    ``chunksize``.

    This function is similar to ``bottle._file_iter_range`` but does not fail
    on missing ``seek()`` attribute (e.g., ``StringIO`` objects).
    """
    try:
        fd.seek(offset)
    except AttributeError:
        # this object does not support ``seek()`` so simply discard the first
        # ``offset - 1`` bytes
        fd.read(offset - 1)
    while length > 0:
        chunk = fd.read(min(length, chunksize))
        if not chunk:
            break
        length -= len(chunk)
        yield chunk


def send_file(content, filename, size=None, timestamp=None):
    """
    Convert file data into an HTTP response.

    This method is used when the file data does not exist on disk, such as when
    it is dynamically generated.

    Because the file does not exist on disk, the basic metadata which is
    usually read from the file itself must be supplied as arguments. The
    ``filename`` argument is the supposed filename of the file data. It is only
    used to set the Content-Type header, and you may safely pass in just the
    extension with leading period.

    The ``size`` argument is the payload size in bytes. For streaming files,
    this can be particularly important as the ranges are calculated baed on
    content length. If ``size`` is omitted, then support for ranges is not
    advertise and ranges are never returned.

    ``timestamp`` is expected to be in seconds since UNIX epoch, and is used to
    calculate Last-Modified HTTP headers, as well as handle If-Modified-Since
    header. If omitted, current time is used, and If-Modified-Since is never
    checked.

    .. note::
        The returned response is a completely new response object.
        Modifying the reponse object in the current request context is not
        going to affect the object returned by this function. You should modify
        the object returned by this function instead.

    Example::

        def some_handler():
            import StringIO
            f = StringIO.StringIO('foo')
            return send_file(f, 'file.txt', 3, 1293281312)

    The code is partly based on ``bottle.static_file``, with the main
    difference being the use of file-like objects instead of files on disk.
    """
    headers = {}
    ctype = get_mimetype(filename)

    if ctype.startswith('text/'):
        # We expect and assume all text files are encoded UTF-8. It's
        # user's job to ensure this is true.
        ctype += '; charset=UTF-8'

    # Set basic headers
    headers['Content-Type'] = ctype
    if size:
        headers['Content-Length'] = size
    headers['Last-Modified'] = format_ts(timestamp)

    # Check if If-Modified-Since header is in request and respond early if so
    if timestamp:
        modsince = request.environ.get('HTTP_IF_MODIFIED_SINCE')
        modsince = modsince and parse_date(modsince.split(';')[0].strip())
        if modsince is not None and modsince >= timestamp:
            headers['Date'] = format_ts()
            return HTTPResponse(status=304, **headers)

    if request.method == 'HEAD':
        # Request is a HEAD, so remove any content body
        content = ''

    if size:
        headers['Accept-Ranges'] = 'bytes'

    ranges = request.environ.get('HTTP_RANGE')
    if ranges and size:
        ranges = list(parse_range_header(ranges, size))
        if not ranges:
            return HTTPError(416, "Request Range Not Satisfiable")
        start, end = ranges[0]
        headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end - 1, size)
        headers['Content-Length'] = str(end - start)
        content = iter_read_range(content, start, end - start)
    return HTTPResponse(content, **headers)


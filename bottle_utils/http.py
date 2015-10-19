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

# We only neeed MIME types for files Outernet will broadcast
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
    """ Guess mime-type based on file's extension

    :param filename:    filename
    :private:
    """
    name, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext[1:], DEFAULT_TYPE)


def format_ts(seconds=None):
    """ Format timestamp expressed as seconds from epoch in RFC format

    If the ``seconds`` argument is omitted, or is ``None``, the current time is
    used.

    :param seconds:     seconds since local system's epoch
    :returns:           formatted timestamp
    :private:
    """
    return time.strftime(TIMESTAMP_FMT, time.gmtime(seconds))


def iter_read_range(fd, offset, length, chunksize=1024*1024):
    """ Like ``bottle._file_iter_range`` but does not fail on ``seek()``

    :param fd:          file-like object that may or may not support ``seek()``
    :param offset:      offset from the beginning in bytes
    :param length:      number of bytes to read
    :param chunksize:   maximum size of the chunk
    :private:
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


def send_file(content, filename, size, timestamp):
    """ Send a file represented by file object as HTTP response

    The code is partly based on ``bottle.static_file``, with the main
    difference being the use of file-like objects instead of files on disk.

    This may be useful when you are generating file contents on the fly. The
    extra metadata must be supplied because we are not dealing with physical
    files here.

    Note that the returned response is a completely new response object.
    Modifying the reponse object in the current request context is not going to
    affect the object returned by this function. You should modify the object
    returned by this function instead.

    Example::

        def some_handler():
            import StringIO
            f = StringIO.StringIO('foo')
            return send_file(f, 'file.txt', 3, 1293281312)

    :param content:     file-like object
    :param filename:    filename to use
    :param size:        file size in bytes
    :param timestamp:   file's timestamp seconds since epoch
    """
    headers = {}
    ctype = get_mimetype(filename)

    if ctype.startswith('text/'):
        # We expect and assume all text files are encoded UTF-8. It's
        # user's job to ensure this is true.
        ctype += '; charset=UTF-8'

    # Set basic headers
    headers['Content-Type'] = ctype
    headers['Content-Length'] = size
    headers['Last-Modified'] = format_ts(timestamp)

    # Check if If-Modified-Since header is in request and respond early if so
    modsince = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    modsince = modsince and parse_date(modsince.split(';')[0].strip())
    if modsince is not None and modsince >= timestamp:
        headers['Date'] = format_ts()
        return HTTPResponse(status=304, **headers)

    if request.method == 'HEAD':
        # Request is a HEAD, so remove any content body
        content = ''

    headers['Accept-Ranges'] = 'bytes'
    ranges = request.environ.get('HTTP_RANGE')
    if ranges:
        ranges = list(parse_range_header(ranges, size))
        if not ranges:
            return HTTPError(416, "Request Range Not Satisfiable")
        start, end = ranges[0]
        headers['Content-Range'] = 'bytes %d-%d/%d' % (start, end - 1, size)
        headers['Content-Length'] = str(end - start)
        content = iter_read_range(content, start, end - start)
    return HTTPResponse(content, **headers)


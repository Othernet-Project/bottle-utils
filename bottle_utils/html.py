"""
helpers.py: helper function for use with templates and bottle framework

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import types
import functools

from decimal import Decimal
from bottle import request, html_escape
from dateutil.parser import parse

from .common import *


SIZES = 'KMGTP'
FERR_CLS = 'form-errors'
FERR_ONE_CLS = 'form-error'
ERR_CLS = 'field-error'


def plur(word, n, plural=lambda n: n != 1,
         convert=lambda w, p: w + 's' if p else w):
    """ Pluralize word based on number of items

    This function takes two optional arguments, ``plural`` and ``convert``,
    which can be customized to change the way plural form is derived from the
    original string. The default implementation is a naive version of English
    language plural, which uses plural form if number is not 1, and derives the
    plural form by simply adding 's' to the word. While this works in most
    cases, it doesn't always work even for English.

    The ``plural`` function takes the value of the ``n`` argument and its
    return value is fed into the ``convert`` function. The latter takes the
    source word as first argument, and return value of ``plural()`` call as
    second argument, and returns a string representing the pluralized word.
    Return value of the ``convert()`` call is returned from this function.

    Example::

        >>> plur('book', 1)
        'book'
        >>> plur('book', 2)
        'books'

        # But it's a bit naive
        >>> plur('box', 2)
        'boxs'

    :param word:    string to pluralize
    :param n:       number of items from which to calculate plurals
    :param plural:  function that returns true if the plural form should be
                    used
    :param convert: function that converts the string to plural
    :returns:       word in appropriate form
    """
    return convert(word, plural(n))


def hsize(size, unit='B', step=1024):
    """ Given size in unit produce size with human-friendly units

    Example::

        >>> hsize(12)
        '12.00 B'
        >>> hsize(1030)
        '1.01 KB'
        >>> hsize(1536)
        '1.50 KB'
        >>> hsize(2097152)
        '2.00 MB'

    :param size:    size in base units
    :param unit:    base unit without prefix
    :param step:    steps for next unit (e.g., 1000 for Kilo, or 1024 for Kilo)
    :returns:       appropriate units
    """
    size = Decimal(size)
    order = -1
    while size > step:
        size /= step
        order += 1
    if order < 0:
        return '%.2f %s' % (round(size, 2), unit)
    return '%.2f %s%s' % (round(size, 2), SIZES[order], unit)


def attr(name, value=None):
    """ Render HTML attribute

    If the value is ``None``, only the attribute name is rendered, otherwise a
    normal 'attribute="value"' pair is returned.

    :param name:    attribute name
    :param value:   optional attribute value
    :returns:       correctly rendered attribute-value pair or attribute name
    """
    if value is not None:
        value = to_unicode(value)
        value = attr_escape(value)
        return '%s="%s"' % (name, value)
    return name


def tag(name, content='', nonclosing=False, **attrs):
    """ Wraps content in a HTML tag with optional attributes

    Any attribute names with any number of leading underscores (e.g., '_class')
    will have the underscores strpped away.

    If content is an iterable, the tag will be generated once per each member.

    :param name:    tag name
    :param content: tag content
    :param attrs:   optional tag attributes
    :returns:       HTML of the tag with its content and attributes
    """
    open_tag = '<%s>' % name
    close_tag = '</%s>' % name
    attrs = ' '.join([attr(k.lstrip('_'), v) for k, v in attrs.items()])
    if attrs:
        open_tag = '<%s %s>' % (name, attrs)
    if nonclosing:
        content = ''
        close_tag = ''
    if not isinstance(content, basestring):
        try:
            return ''.join(['%s%s%s' % (open_tag, c, close_tag)
                            for c in content])
        except TypeError:
            pass
    return '%s%s%s' % (open_tag, content, close_tag)


SPAN = functools.partial(tag, 'span')
UL = functools.partial(tag, 'ul')
LI = functools.partial(tag, 'li')
P = functools.partial(tag, 'p')
A = functools.partial(tag, 'a')
INPUT = functools.partial(tag, 'input', nonclosing=True)
BUTTON = functools.partial(tag, 'button')
SUBMIT = functools.partial(BUTTON, _type='submit')
HIDDEN = lambda n, v: INPUT(_name=n, value=v, _type='hidden')
TEXTAREA = functools.partial(tag, 'textarea')
BUTTON = functools.partial(tag, 'button')
OPTION = functools.partial(tag, 'option')
SELECT = functools.partial(tag, 'select')


def vinput(name, values, **attrs):
    """ Render input with value """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return INPUT(_name=name, **attrs)
    return INPUT(_name=name, value=value, **attrs)


def varea(name, values, **attrs):
    """ Render textarea with value """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return TEXTAREA(_name=name, **attrs)
    return TEXTAREA(value, _name=name, **attrs)


def vcheckbox(name, value, values, default=False, **attrs):
    """ Render checkbox with value """
    if name in values:
        try:
            values = values.getall(name)
        except AttributeError:
            values = values.get(name, [])
        if isinstance(values, basestring):
            if value == values:
                attrs['checked'] = None
        elif value in values:
            attrs['checked'] = None
    elif default:
        if default:
            attrs['checked'] = None
    elif 'checked' in attrs:
        del attrs['checked']
    return INPUT(_type='checkbox', _id=name, _name=name, value=value, **attrs)


def vselect(name, choices, values, **attrs):
    """ Render select list with value preselected """
    value = values.get(name)
    options = []
    for val, label in choices:
        if val == value:
            options.append(OPTION(label, value=val, selected=None))
        else:
            options.append(OPTION(label, value=val))
    return SELECT(''.join(options), _id=name, _name=name, **attrs)


def link_other(label, url, path, wrapper=None, **kwargs):
    """ Only wrap label in anchor if given URL is not the path

    :param label:   label of the link
    :param url:     URL to which label should be linked
    :param path:    path to test URL against
    :param wrapper: function that should be used to wrap the label if URL
                    matches the path (i.e., anchor is not being rendered)
    """
    if url == path:
        try:
            return wrapper(label, **kwargs)
        except TypeError:
            return label
    return A(label, href=url, **kwargs)


def field_error(errors_dict, field_name):
    """ Renders an error if error dict has one for the field

    :param errors_dict:     dict-like object containing field-name-message
                            mappings
    :param field_name:      name of the field to look up in the dict
    :returns:               HTML of the error message if one is found,
                            otherwise empty string
    """
    try:
        return SPAN(html_escape(errors_dict[field_name]), _class=ERR_CLS)
    except KeyError:
        return ''


def form_errors(errors_dict):
    """ Renders a form error if dict has one

    Form errors must be contained within a special key '_'. The error messages
    can be either an iterable or single string. If it is a single string, it
    will be rendered as a ``span``. Otherwise, a series of ``li`` elements will
    be rendered.
    """
    try:
        return UL(LI(html_escape(errors_dict['_']), _class=FERR_ONE_CLS),
                  _class=FERR_CLS)
    except KeyError:
        return ''
    except TypeError:
        return P(SPAN(html_escape(errors_dict['_']), _class=FERR_ONE_CLS),
                 _class=FERR_CLS)


def trunc(s, n):
    """ Trucante string at ``n`` characters """
    if len(s) <= n:
        return s
    return s[:n] + '...'


def yesno(val, yes='yes', no='no'):
    """ Return ``yes`` or ``no`` depending on whether ``val`` is ``True`` """
    return yes if val else no


def strft(ts, fmt):
    """ Format datetime object or timestamp as string using provided format """
    return parse(ts).strftime(fmt)



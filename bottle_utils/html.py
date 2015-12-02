# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools

try:
    from urllib import quote, unquote
except ImportError:
    from urllib.parse import quote, unquote

from decimal import Decimal
from dateutil.parser import parse
from bottle import request, MultiDict, _parse_qsl

from .common import (to_bytes, to_unicode, attr_escape, html_escape,
                     basestring, unicode)


SIZES = 'KMGTP'
FERR_CLS = 'form-errors'
FERR_ONE_CLS = 'form-error'
ERR_CLS = 'field-error'


urlquote = lambda value: quote(to_bytes(value))
urlunquote = lambda value: to_unicode(unquote(value))


class QueryDict(MultiDict):
    """
    Represents a query string in ``bottle.MultiDict`` format.

    This class differs from the base ``bottle.MultiDict`` class in two ways.
    First, it is instantiated with raw query string, rather than a list of
    two-tuples::

        >>> q = QueryDict('a=1&b=2')

    The query string is parsed and converted to ``MultiDict`` format. This
    works exactly the same way as ``request.query``.

    Second difference is the way string coercion is handled. ``QueryDict``
    instances can be converted back into a query string by coercing them into
    string or bytestring::

        >>> str(q)
        'a=1&b=2'

    The coercion also happens when using the ``+`` operator to concatenate with
    other strings::

        >>> 'foo' + q
        'foo?a=1&b=2'

    Notice that the '?' character is inserted when using the ``+`` operator.

    .. note::
        When converting back to string, the order of parameters in the
        resulting query string may differ from the original.

    Furthermore, additional methods have been added to provide chaining
    capability in conjunction with ``*_qparam()`` functions in this module.

    For instance::

        >>> q = QueryDict('a=1&b=2')
        >>> q.del_qparam('a').set_qparam(b=3).add_qparam(d=2, k=12)
        >>> str(s)
        'b=3&d=2&k=12'

    When used with functions like :py:func:`~add_qparam`, this provides a more
    intuitive API::

        >>> qs = 'a=1&b=2'
        >>> q = add_qparam(qs, c=2).set_qparam(a=2)
        >>> str(q)
        'a=2&b=2&c=2'

    Since this class is a ``bottle.MultiDict`` subclass, you can expect it to
    behave the same way as a regular ``MultiDict`` object. You can assign
    values to keys, get values by key, get all items as a list of key-value
    tuples, and so on. Please consult the Bottle documentation for more
    information on how ``MultiDict`` objects work.
    """

    def __init__(self, qs=''):
        super(QueryDict, self).__init__(_parse_qsl(qs))

    def add_qparam(self, **params):
        """
        Add query parameter. Any keyword arguments passed to this function will
        be converted to query parameters.

        Returns the instance for further chaining.
        """
        for param, value in params.items():
            self.append(param, to_unicode(value))
        return self

    def set_qparam(self, **params):
        """
        Replace or add parameter. Any keyword arguments passed to this function
        will be converted to query parameters.

        Returns the instance for further chaining.
        """
        for param, value in params.items():
            self.replace(param, to_unicode(value))
        return self

    def del_qparam(self, *params):
        """
        Remove a query parameter. Takes any number of parameter names to be
        removed.

        Returns the instance for further chaining.
        """
        for param in params:
            try:
                del self[param]
            except KeyError:
                pass
        return self

    def to_qs(self):
        """
        Return the string representation of the query string with prepended
        '?' character.
        """
        return '?' + str(self)

    def __radd__(self, other):
        return other + str(self.to_qs())

    def __add__(self, other):
        return str(self.to_qs()) + other

    def __str__(self):
        return '&'.join(['{}={}'.format(urlquote(k), urlquote(v))
                         for k, v in self.allitems()])


# DATA FORMATTING


def plur(word, n, plural=lambda n: n != 1,
         convert=lambda w, p: w + 's' if p else w):
    """
    Pluralize word based on number of items. This function provides rudimentary
    pluralization support. It is quite flexible, but not a replacement for
    functions like ``ngettext``.

    This function takes two optional arguments, ``plural()`` and ``convert()``,
    which can be customized to change the way plural form is derived from the
    original string. The default implementation is a naive version of English
    language plural, which uses plural form if number is not 1, and derives the
    plural form by simply adding 's' to the word. While this works in most
    cases, it doesn't always work even for English.

    The ``plural(n)`` function takes the value of the ``n`` argument and its
    return value is fed into the ``convert()`` function. The latter takes the
    source word as first argument, and return value of ``plural()`` call as
    second argument, and returns a string representing the pluralized word.
    Return value of the ``convert(w, p)`` call is returned from this function.

    Here are some simple examples::

        >>> plur('book', 1)
        'book'
        >>> plur('book', 2)
        'books'

        # But it's a bit naive
        >>> plur('box', 2)
        'boxs'

    The latter can be fixed like this::

        >>> exceptions = ['box']
        >>> def pluralize(word, is_plural):
        ...    if not is_plural:
        ...        return word
        ...    if word in exceptions:
        ...        return word + 'es'
        ...    return word + 's'
        >>> plur('book', 2)
        'books'
        >>> plur('box', 2, convert=pluralize)
        'boxes'

    """
    return convert(word, plural(n))


def hsize(size, unit='B', step=1024, rounding=2, sep=' '):
    """
    Given size in unit produce size with human-friendly units. This is a simple
    formatting function that takes a value, a unit in which the value is
    expressed, and the size of multiple (kilo, mega, giga, etc).

    This function rounds values to 2 decimal places and does not handle
    fractions. It also uses metric prefixes (K, M, G, etc) and only goes up to
    Peta (P, quadrillion) prefix. The number of decimal places can be
    customized using the ``rounding`` argument.

    The size multiple (``step`` parameter) is 1024 by default, suitable for
    expressing values related to size of data on disk.

    The ``sep`` argument represents a separator between values and units.

    Example::

        >>> hsize(12)
        '12.00 B'
        >>> hsize(1030)
        '1.01 KB'
        >>> hsize(1536)
        '1.50 KB'
        >>> hsize(2097152)
        '2.00 MB'
        >>> hsize(12, sep='')
        '12.00B'

    """
    size = Decimal(size)
    order = -1
    while size > step:
        size /= step
        order += 1
    if order < 0:
        return '%.{}f%s%s'.format(rounding) % (round(size, rounding), sep,
                                               unit)
    return '%.{}f%s%s%s'.format(rounding) % (round(size, rounding), sep,
                                             SIZES[order], unit)


def trunc(s, chars):
    """
    Trucante string at ``n`` characters. This function hard-trucates a string
    at specified number of characters and appends an elipsis to the end.

    The truncating does not take into account words or markup. Elipsis is not
    appended if the string is shorter than the specified number of characters.
    ::

        >>> trunc('foobarbaz', 6)
        'foobar...'

    .. note::

       Keep in mind that the trucated string is always 3 characters longer than
       ``n`` because of the appended elipsis.

    """
    if len(s) <= chars:
        return s
    return s[:chars] + '...'


def yesno(val, yes='yes', no='no'):
    """
    Return ``yes`` or ``no`` depending on value. This function takes the value
    and returns either yes or no depending on whether the value evaluates to
    ``True``.

    Examples::

        >>> yesno(True)
        'yes'
        >>> yesno(False)
        'no'
        >>> yesno(True, 'available', 'not available')
        'available'

    """
    return yes if val else no


def strft(ts, fmt):
    """
    Reformat string datestamp/timestamp. This function parses a string
    representation of a date and/or time and reformats it using specified
    format.

    The format is standard strftime format used in Python's
    ``datetime.datetime.strftime()`` call.

    Actual parsing of the input is delegated to
    `python-dateutil <https://pypi.python.org/pypi/python-dateutil>`_ library.

    """
    return parse(ts).strftime(fmt)


# HTML


def attr(name, value=None):
    """
    Render HTML attribute. This function is used as part of :py:func:`~tag`
    function to render HTML attributes, but can be used on its own as well. It
    converts the value into Unicode string and sanitizes it before returning
    the markup.

    Basic usage may look like this::

        >>> attr('src', '/images?src=foo.png&w=12')
        'src="/images?src=foo.png&amp;w=12"'

    All attribute values are double-quoted and any double quotes found inside
    the value are escaped. User-supplied values can be used reasonably safely.

    If the value is ``None``, only the attribute name is rendered, otherwise a
    normal 'attribute="value"' pair is returned::

        >>> attr('src', None)
        'src'
        >>> attr('src', '')
        'src=""'

    Therefore, to suppress attribute values completely (i.e., not even have the
    ``=""`` part, use ``None`` as the value.

    """
    if value is not None:
        value = to_unicode(value)
        value = attr_escape(value)
        return '%s="%s"' % (name, value)
    return name


def tag(name, content='', nonclosing=False, **attrs):
    """
    Wraps content in a HTML tag with optional attributes. This function
    provides a Pythonic interface for writing HTML tags with a few bells and
    whistles.

    The basic usage looks like this::

        >>> tag('p', 'content', _class="note", _id="note1")
        '<p class="note" id="note1">content</p>'

    Any attribute names with any number of leading underscores (e.g., '_class')
    will have the underscores strpped away.

    If content is an iterable, the tag will be generated once per each member.

        >>> tag('span', ['a', 'b', 'c'])
        '<span>a</span><span>b</span><span>c</span>'

    It does not sanitize the tag names, though, so it is possible to specify
    invalid tag names::

        >>> tag('not valid')
        '<not valid></not valid>

    .. warning::
        Please ensure that ``name`` argument does not come from user-specified
        data, or, if it does, that it is properly sanitized (best way is to use
        a whitelist of allowed names).

    Because attributes are specified using keyword arguments, which are then
    treated as a dictionary, there is no guarantee of attribute order. If
    attribute order is important, don't use this function.

    This module contains a few partially applied aliases for this function.
    These mostly have hard-wired first argument (tag name), and are all
    uppercase:

    - ``A`` - alias for ``<a>`` tag
    - ``BUTTON`` - alias for ``<button>`` tag
    - ``HIDDEN`` - alias for ``<input>`` tag with ``type="hidden"`` attribute
    - ``INPUT`` - alias for ``<input>`` tag with ``nonclosing`` set to ``True``
    - ``LI`` - alias for ``<li>`` tag
    - ``OPTION`` - alias for ``<option>`` tag
    - ``P`` - alias for ``<p>`` tag
    - ``SELECT`` - alias for ``<select>`` tag
    - ``SPAN`` - alias for ``<span>`` tag
    - ``SUBMIT`` - alias for ``<button>`` tag with ``type="submit"`` attribute
    - ``TEXTAREA`` - alias for ``<textarea>`` tag
    - ``UL`` - alias for ``<ul>`` tag

    """
    open_tag = '<%s>' % name
    close_tag = '</%s>' % name
    attrs = ' '.join([attr(k.lstrip('_'), to_unicode(v))
                      for k, v in attrs.items()])
    if attrs:
        open_tag = '<%s %s>' % (name, attrs)
    if nonclosing:
        content = ''
        close_tag = ''
    if not isinstance(content, basestring):
        try:
            return ''.join(['%s%s%s' % (open_tag, to_unicode(c), close_tag)
                            for c in content])
        except TypeError:
            pass
    return '%s%s%s' % (open_tag, to_unicode(content), close_tag)


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
    """
    Render input with bound value. This function can be used to bind values to
    form inputs. By default it will result in HTML markup for a generic input.
    The generated input has a ``name`` attribute set to specified name, and
    an ``id`` attribute that has the same value.
    ::
        >>> vinput('foo', {})
        '<input name="foo" id="foo">'

    If the supplied dictionary of field values contains a key that matches the
    specified name (case-sensitive), the value of that key will be used as the
    value of the input::

        >>> vinput('foo', {'foo': 'bar'})
        '<input name="foo" id="foo" value="bar">'

    All values are properly sanitized before they are added to the markup.

    Any additional keyword arguments that are passed to this function are
    passed on the :py:func:`~tag` function. Since the generated input markup is
    for generic text input, some of the other usual input types can be
    specified using ``_type`` parameter::

        >>> input('foo', {}, _type='email')
        '<input name="foo" id="foo" type="email">'

    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return INPUT(_name=name, **attrs)
    return INPUT(_name=name, value=value, **attrs)


def varea(name, values, **attrs):
    """
    Render textarea with bound value. Textareas use a somewhat different markup
    to that of regular inputs, so a separate function is used for binding
    values to this form control.::

        >>> varea('foo', {'foo': 'bar'})
        '<textarea name="foo" id="foo">bar</textarea>'

    This function works the same way as :py:func:`~vinput` function, so please
    look at it for more information. The primary difference is in the generated
    markup.

    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return TEXTAREA(_name=name, **attrs)
    return TEXTAREA(value, _name=name, **attrs)


def vcheckbox(name, value, values, default=False, **attrs):
    """
    Render checkbox with bound value. This function renders a checkbox which is
    checked or unchecked depending on whether its own name-value combination
    appears in the provided form values dictionary.

    Because there are many ways to think about checkboxes in general, this
    particular function may or may not work for you. It treats checkboxes as a
    list of alues which are all named the same.

    Let's say we have markup that looks like this::

        <input type="checkbox" name="foo" value="1">
        <input type="checkbox" name="foo" value="2">
        <input type="checkbox" name="foo" value="3">

    If user checks all of them, we consider it a list ``foo=['1', '2', '3']``.
    If user checks only the first and last, we have ``foo=['1', '3']``. And so
    on.

    This function assumes that you are using  this pattern.

    The ``values`` map can either map the checkbox name to a single value, or a
    list of multiple values. In the former case, if the single value matches
    the value of the checkbox, the checkbox is checked. In the latter case, if
    value of the checkbox is found in the list of values, the checkbox is
    checked.::

        >>> vcheckbox('foo', 'bar', {'foo': 'bar'})
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'
        >>> vcheckbox('foo', 'bar', {'foo': ['foo', 'bar', 'baz']})
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'
        >>> vcheckbox('foo', 'bar', {'foo': ['foo', 'baz']})
        '<input type="checkbox" name="foo" id="foo" value="bar">'

    When the field values dictionary doesn't contain a key that matches the
    checkbox name, the value of ``default`` keyword argument determines whether
    the checkbox should be checked::

        >>> vcheckbox('foo', 'bar', {}, default=True)
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'

    """
    attrs.setdefault('_id', name)
    if name in values:
        try:
            values = values.getall(name)
        except AttributeError:
            values = values.get(name, [])
        if isinstance(values, basestring):
            if unicode(value) == unicode(values):
                attrs['checked'] = None
        elif unicode(value) in [unicode(v) for v in values]:
            attrs['checked'] = None
    elif default:
        if default:
            attrs['checked'] = None
    elif 'checked' in attrs:
        del attrs['checked']
    return INPUT(_type='checkbox', _name=name, value=value, **attrs)


def vselect(name, choices, values, empty=None, **attrs):
    """
    Render select list with bound value. This function renders the select list
    with option elements with appropriate element selected based on field
    values that are passed.

    The values and labels for option elemnets are specified using an iterable
    of two-tuples::

        >>> vselect('foo', ((1, 'one'), (2, 'two'),), {})
        '<select name="foo" id="foo"><option value="1">one</option><option...'

    There is no mechanism for default value past what browsers support, so you
    should generally assume that most browsers will render the select with
    frist value preselected. Using an empty string or ``None`` as option value
    will render an option element without value::

        >>> vselect('foo', ((None, '---'), (1, 'one'),), {})
        '<select name="foo" id="foo"><option value>---</option><option val...'
        >>> vselect('foo', (('', '---'), (1, 'one'),), {})
        '<select name="foo" id="foo"><option value="">---</option><option ...'

    When specifying values, keep in mind that only ``None`` is special, in that
    it will crete a ``value`` attribute without any value. All other Python
    types become strings in the HTML markup, and are submitted as such. You
    will need to convert the values back to their appropriate Python type
    manually.

    If the choices iterable does not contain an element representing the empty
    value (``None``), you can specify it using the ``empty`` parameter. The
    argument for ``empty`` should be a label, and the matching value is
    ``None``. The emtpy value is always inseted at the beginning of the list.

    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    options = []
    for val, label in choices:
        if unicode(val) == unicode(value):
            options.append(OPTION(label, value=val, selected=None))
        else:
            options.append(OPTION(label, value=val))
    if empty:
        options.insert(0, OPTION(empty, value=None))
    return SELECT(''.join(options), _name=name, **attrs)


def form(method=None, action=None, csrf=False, multipart=False, **attrs):
    """
    Render open form tag. This function renders the open form tag with
    additional features, such as faux HTTP methods, CSRF token, and multipart
    support.

    All parameters are optional. Using this function without any argument has
    the same effect as naked form tag without any attributes.

    Method names can be either lowercase or uppercase.

    The methods other than GET and POST are faked using a hidden input with
    ``_method`` name and uppercase name of the HTTP method. The form will use
    POST method in this case. Server-side support is required for this feature
    to work.

    Any additional keyword arguments will be used as attributes for the form
    tag.

    """
    method = method and method.upper()
    if not method:
        faux_method = False
    elif method in ['GET', 'POST']:
        attrs['method'] = method
        faux_method = False
    else:
        attrs['method'] = 'POST'
        faux_method = True
    if multipart:
        attrs['enctype'] = 'multipart/form-data'
    if action is not None:
        attrs['action'] = action
    s = tag('form', nonclosing=True, **attrs)
    if faux_method:
        s += HIDDEN('_method', method)
    if csrf:
        # Import csrf_tag here to avoid circular dependency, since the csrf
        # module uses functions from this module
        from .csrf import csrf_tag
        s += csrf_tag()
    return s


def link_other(label, url, path, wrapper=SPAN, **kwargs):
    """
    Only wrap label in anchor if given target URL, ``url``, does not match the
    ``path``. Given a label, this function will match the page URL against the
    path to which the anchor should point, and generate the anchor element
    markup as necessary. If the paths, match, ``wrapper`` will be used to
    generate the markup around the label.

    Any additional keyword arguments are passed to the function that generates
    the anchor markup, which is :py:func:`~A` alias of the :py:func:`~tag`
    function.

    If the URLs match (meaning the page URL matches the target path), the label
    will be passed to the wrapper function. The default wrapper function is
    :py:func:`~SPAN`, so the label is wrapped in SPAN tag when the URLs
    matches.::

        >>> link_other('foo', '/here', '/there')
        '<a href="/target">foo</a>'
        >>> link_other('foo', '/there', '/there')
        '<span>foo</span>'

    You can customize the appearance of the label in the case URLs match by
    customizing the wrapper::

        >>> link_other('foo', '/there', '/there',
        ...            wrapper=lambda l, **kw: l + 'bar')
        'foobar'

    Note that the wrapper lambda function has wild-card keyword arguments. The
    wrapper function accepts the same extra keyword arguments that the anchor
    function does, so if you have common classes and similar attributes, you
    can specify them as extra keyword arguments and use any of the helper
    functions in this module.::

        >>> link_other('foo', '/here', '/there', wrapper=BUTTON, _class='cls')
        '<a class="cls" href="/target">foo</a>'
        >>> link_other('foo', '/there', '/there', wrapper=BUTTON, _class='cls')
        '<button class="cls">foo</button>'

    """
    if url == path:
        return wrapper(label, **kwargs)
    return A(label, href=url, **kwargs)


def quote_dict(mapping):
    """URL quote keys and values of the passed in dict-like object.

    :param mapping:     ``bottle.MultiDict`` or ``dict``-like object
    :returns:           dict with url quoted values
    """
    try:
        pairs = mapping.allitems()
    except AttributeError:
        pairs = mapping.items()
    qdict = QueryDict()
    for k, v in pairs:
        qdict[urlquote(k)] = urlquote(v)
    return qdict


def quoted_url(route, **params):
    """Return matching URL with it's query parameters quoted."""
    return request.app.get_url(route, **quote_dict(params))


def to_qs(mapping):
    """
    Convert a mapping object to query string appended to current path. This
    function takes a ``bottle.MultiDict`` object or a ``dict``-like object that
    supports ``items()`` call, and converts it to a query string appeneded to
    the path in the current request context.

    The values for each parameter is encoded as UTF-8 and escaped.

    """
    qs = ['{}={}'.format(k, v) for k, v in quote_dict(mapping).allitems()]
    return request.path + '?' + '&'.join(qs)


_to_qdict = lambda qs: QueryDict(qs) if isinstance(qs, basestring) else qs


def add_qparam(qs=None, **params):
    """
    Add parameter to query string

    If query string is omitted ``request.query_string`` is used.

    Any keyword arguments passed to this function will be converted to query
    parameters.

    The returned object is a :py:class:`~QueryDict` instance, which is a
    ``bottle.MultiDict`` subclass.

    Example::

        >>> q = add_qparam('a=1', b=2)
        >>> str(q)
        'a=1&b=2'
        >> q = add_qparam('a=1', a=2)
        >>> str(q)
        'a=1&a=2'

    """
    qs = qs or request.query_string
    qs = _to_qdict(qs)
    return qs.add_qparam(**params)


def set_qparam(qs=None, **params):
    """
    Replace or add parameters to query string

    If query string is omitted ``request.query_string`` is used.

    Any keyword arguments passed to this function will be converted to query
    parameters.

    The returned object is a :py:class:`~QueryDict` instance, which is a
    ``bottle.MultiDict`` subclass.

    """
    qs = qs or request.query_string
    qs = _to_qdict(qs)
    return qs.set_qparam(**params)


def del_qparam(qs=None, *params):
    """
    Remove query string parameters

    If query string is ``None`` or empty, ``request.query_string`` is used.

    Second and subsequent positional arguments are query parameter names to be
    removed from the query string.

    The returned object is a :py:class:`~QueryDict` instance, which is a
    ``bottle.MultiDict`` subclass.

    """
    qs = qs or request.query_string
    qs = _to_qdict(qs)
    return qs.del_qparam(*params)


def perc_range(n, min_val, max_val, rounding=2):
    """
    Return percentage of `n` within `min_val` to `max_val` range. The
    ``rounding`` argument is used to specify the number of decimal places to
    include after the floating point.

    Example::

        >>> perc_range(40, 20, 60)
        50

    """
    return round(
        min([1, max([0, n - min_val]) / (max_val - min_val)]) * 100, rounding)

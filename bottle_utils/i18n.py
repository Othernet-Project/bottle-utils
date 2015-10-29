import gettext
import functools

from warnings import warn

from bottle import (redirect,
                    request,
                    response,
                    template,
                    BaseTemplate,
                    DictMixin)

from .lazy import lazy
from .html import quoted_url
from .common import to_unicode


CONTEXT_SEPARATOR = '\x04'


def dummy_gettext(message):
    """
    Mimic ``gettext()`` function. This is a passthrough function with the same
    signature as ``gettext()``. It can be used to simulate translation for
    applications that are untranslated, without the overhead of calling the
    real ``gettext()``.
    """
    return message


def dummy_ngettext(singular, plural, n):
    """
    Mimic ``ngettext()`` function. This is a passthrough function with the
    same signature as ``ngettext()``. It can be used to simulate translation
    for applications that are untranslated, without the overhead of calling the
    real ``ngettext()``.

    This function returns the verbatim singular message if ``n`` is 1,
    otherwise the verbatim plural message.
    """
    if n == 1:
        return singular
    return plural


def dummy_pgettext(context, message):
    """
    Mimic ``pgettext()`` function. This is a passthrough function with the same
    signature as ``pgettext()``. It can be used to simulate translation for
    applications that are untranslated, without the overhead of calling the
    real ``pgettext()`.
    """
    return dummy_gettext(message)


def dummy_npgettext(context, singular, plural, n):
    """
    Mimic ``npgettext()`` function. This is a passthrough function with teh
    same signature as ``npgettext()``. It can be used to simulate translation
    for applications that are untranslated, without the overhead of calling the
    real ``npgettext()`` function.
    """
    return dummy_ngettext(singular, plural, n)


@lazy
def lazy_gettext(message):
    """
    Lazily evaluated version of ``gettext()``.

    This function uses the appropriate Gettext API object based on the value of
    ``bottle.request.gettext`` set by the plugin. It will fail with
    ``AttributeError`` exception if the plugin is not installed.
    """
    gettext = request.gettext.gettext
    return to_unicode(gettext(message))


@lazy
def lazy_ngettext(singular, plural, n):
    """
    Lazily evaluated version of ``ngettext()``.

    This function uses the appropriate Gettext API object based on the value of
    ``bottle.request.gettext`` set by the plugin. It will fail with
    ``AttributeError`` exception if the plugin is not installed.
    """
    ngettext = request.gettext.ngettext
    return to_unicode(ngettext(singular, plural, n))


def lazy_pgettext(context, message):
    """
    :py:func:`~lazy_gettext` wrapper with message context.

    This function is a wrapper around :py:func:`~lazy_gettext` that provides
    message context. It is useful in situations where short messages (usually
    one word) are used in several different contexts for which separate
    translations may be needed in different languages.

    The function itself is not lazily evaluated, but its return value comes
    from ``lazy_gettext()`` call, and it is effectively lazy as a result.
    """
    message = '%s%s%s' % (context, CONTEXT_SEPARATOR, message)
    return lazy_gettext(message)


def lazy_npgettext(context, singular, plural, n):
    """
    :py:func:`bottle_utils.i18n.lazy_ngettext` wrapper with message context.

    This function is a wrapper around
    :py:func:`bottle_utils.i18n.lazy_ngettext`
    that provides message context. It is useful in situations where messages
    are used in several different contexts for which separate translations may
    be required for different languages.

    The function itself is not lazy, but it returns the return value of
    ``lazy_ngettext()``, and it is effectively lazy. Hence the name.
    """
    singular = '%s%s%s' % (context, CONTEXT_SEPARATOR, singular)
    plural = '%s%s%s' % (context, CONTEXT_SEPARATOR, plural)
    return lazy_ngettext(singular, plural, n)


def full_path():
    """
    Calculate full path including query string for current request. This is a
    helper function used by :py:func:`~i18n_path`. It uses the current request
    context to obtain information about the path.
    """
    path = request.fullpath
    qs = request.query_string
    if qs:
        return '%s?%s' % (path, qs)
    return path


@lazy
def i18n_path(path=None, locale=None):
    """
    Return current request path or specified path for given or current locale.
    This function can be used to obtain paths for different locales.

    If no ``path`` argument is passed, the :py:func:`~full_path` is called to
    obtain the full path for current request.

    If ``locale`` argument is omitted, current locale is used.
    """
    path = path or full_path()
    locale = locale or request.locale
    if not locale:
        # This is a bit unexpected, but it obviously can happen
        return path
    return '/{}{}'.format(locale, path)


@lazy
def i18n_url(route, **params):
    """
    Return a named route in localized form. This function is a light wrapper
    around Bottle's ``get_url()`` function. It passes the result to
    :py:func:`~i18n_path`.

    If ``locale`` keyword argument is passed, it will be used instead of the
    currently selected locale.
    """
    locale = params.pop('locale', request.locale)
    path = quoted_url(route, **params)
    return i18n_path(path, locale=locale)


def i18n_view(tpl_base_name=None, **defaults):
    """
    Renders a template with locale name as suffix. Unlike the normal view
    decorator, the template name should not have an extension. The locale names
    are appended to the base template name using underscore ('_') as separator,
    and lower-case locale identifier.

    Any additional keyword arguments are used as default template variables.

    For example::

        @i18n_view('foo')
        def render_foo():
            # Renders 'foo_en' for English locale, 'foo_fr' for French, etc.
            return
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                locale = request.locale
                tpl_name = '%s_%s' % (tpl_base_name, locale.lower())
            except AttributeError:
                tpl_name = tpl_base_name
            tplvars = defaults.copy()
            result = func(*args, **kwargs)
            if isinstance(result, (dict, DictMixin)):
                tplvars.update(result)
                return template(tpl_name, **tplvars)
            elif result is None:
                return template(tpl_name, **tplvars)
            return result
        return wrapper
    return decorator


class I18NWarning(RuntimeWarning):
    pass


class I18NPlugin(object):
    """
    Bottle plugin and WSGI middleware for handling i18n routes.  This class is
    a middleware. However, if the ``app`` argument is a ``Bottle`` object
    (bottle app), it will also install itself as a plugin.  The plugin follows
    the `version 2 API <http://bottlepy.org/docs/0.12/plugindev.html>`_ and
    implements the :py:meth:`~apply` method which applies the plugin to all
    routes. The plugin and middleware parts were merged into one class because
    they depend on each other and can't really be used separately.

    During initialization, the class will set up references to locales,
    directory paths, and build a mapping between locale names and appropriate
    gettext translation APIs. The translation APIs are created using the
    ``gettext.translation()`` call. This call tries to access matching .mo file
    in the locale directory, and will emit a warning if such file is not found.
    If a .mo file does not exist for a given locale, or it is not readable, the
    API for that locale will be downgraded to generic `gettext API
    <https://docs.python.org/3.4/library/gettext.html>`_.

    The class will also update the ``bottle.BaseTemplate.defaults`` dict with
    translation-related methods so they are always available in templates (at
    least those that are rendered using bottle's API. The following variables
    become available in all templates:

    - ``_``: alias for :py:func:`~lazy_gettext`
    - ``gettext``: alias for :py:func:`~lazy_gettext`
    - ``ngettext``: alias for :py:func:`~lazy_ngettext`
    - ``pgettext``: alias for :py:func:`~lazy_pgettext`
    - ``npgettext``: alias for :py:func:`~lazy_pngettext`
    - ``languages``: iterable containing available languages as ``(locale,
      name)`` tuples

    In addition, two functions for generating i18n-specific paths are added to
    the default context:

    - :py:func:`~i18n_path`
    - :py:func:`~i18n_url`

    The middleware itself derives the desired locale from the URL. It does not
    read cookies or headers. It only looks for the ``/ll_cc/`` prefix where
    ``ll`` is the two-ltter language ID, and ``cc`` is country code. If it
    finds such a prefix, it will set the locale in the envionment dict
    (``LOCALE`` key) and fix the path so it doesn't include the prefix. This
    allows the bottle app to have routes matching any number of locales. If it
    doesn't find the prefix, it will redirect to the default locale.

    If there is no appropriate locale, and ``LOCALE`` key is therfore set to
    ``None``, the plugin will automatically respond with a 302 redirect to a
    location of the default locale.

    The plugin reads the ``LOCALE`` key set by the middleware, and aliases the
    API for that locale as ``request.gettext``. It also sets ``request.locale``
    attribute to the selected locale. These attributes are used by the
    :py:func:`~lazy_gettext`` and :py:func:`~lazy_ngettext`, as well as
    :py:func:`~i18n_path` and :py:func:`~i18n_url` functions.

    The plugin installation during initialization can be competely suppressed,
    if you wish (e.g., you wish to apply the plugin yourself some other way).

    The locale directory should be in a format which ``gettext.translations()``
    understands. This is a path that contains a subtree matching this format::

        locale_dir/LANG/LC_MESSAGES/DOMAIN.mo

    The ``LANG`` should match any of the supported languages, and ``DOMAIN``
    should match the specified domain.
    """

    # Bottle plugin name
    name = 'i18n'
    # Bottle plugin API version
    api = 2

    def __init__(self, app, langs, default_locale, locale_dir,
                 domain='messages', noplugin=False):
        # The original bottle application object is accessible as ``app``
        # attribute after initialization.
        self.app = app

        # Supported languages as iterable of `(locale, native_name)` tuples.
        self.langs = langs

        # Supported locales (calculated based on ``langs`` iterable).
        self.locales = [lang[0] for lang in langs]

        # Default locale.
        self.default_locale = default_locale

        # Directory that stores ``.po`` and ``.mo`` files.
        self.locale_dir = locale_dir

        # Domain of the translation.
        self.domain = domain

        # A dictionary that maps locales to ``gettext.translation()`` objects
        # for each locale. Appropriate API object is selected from each
        self.gettext_apis = {}

        # Prepare gettext class-based APIs for consumption
        for locale in self.locales:
            try:
                api = gettext.translation(domain, locale_dir,
                                          languages=[locale])
            except OSError:
                api = gettext
                warn(I18NWarning("No MO file found for '%s' locale" % locale))
            self.gettext_apis[locale] = api

        # Provide translation methods to templates
        BaseTemplate.defaults.update({
            '_': lazy_gettext,
            'gettext': lazy_gettext,
            'ngettext': lazy_ngettext,
            'pgettext': lazy_pgettext,
            'npgettext': lazy_npgettext,
            'i18n_path': i18n_path,
            'i18n_url': i18n_url,
            'languages': langs,
        })

        if noplugin:
            return
        try:
            self.install_plugin()
        except AttributeError:
            # It's not strictly necessary to install the plugin automatically
            # like this, especially if there are other WSGI middleware in the
            # stack. We should still warn. It may be unintentional.
            warn(I18NWarning('I18NPlugin: Not a bottle app. Skipping '
                             'plugin installation.'))

    def __call__(self, e, h):
        path = e['PATH_INFO']
        e['LOCALE'] = locale = self.match_locale(path)
        e['ORIGINAL_PATH'] = path
        if locale:
            e['PATH_INFO'] = self.strip_prefix(path, locale)
        return self.app(e, h)

    def install_plugin(self, app=None):
        app = app or self.app
        app.install(self)

    def apply(self, callback, route):
        try:
            ignored = route.config.get('no_i18n', False)
        except AttributeError:
            ignored = False

        def wrapper(*args, **kwargs):
            request.original_path = request.environ.get('ORIGINAL_PATH',
                                                        request.fullpath)
            query_string = request.environ.get('QUERY_STRING')
            if query_string:
                request.original_path = '{0}?{1}'.format(request.original_path,
                                                         query_string)
            default_locale = request.get_cookie('locale', self.default_locale)
            if not ignored:
                request.default_locale = default_locale
                request.locale = locale = request.environ.get('LOCALE')
                if locale:
                    response.set_cookie('locale', locale, path='/')
                if locale not in self.locales:
                    # If no locale had been specified, redirect to default one
                    path = request.original_path
                    redirect(i18n_path(path, default_locale))
                else:
                    request.gettext = self.gettext_apis[locale]
            else:
                # Dummy translation is used for paths which are excepted from
                # i18n plugin.
                request.gettext = gettext.NullTranslations()
                request.locale = default_locale

            return callback(*args, **kwargs)
        return wrapper

    def match_locale(self, path):
        """
        Match the locale based on prefix in request path. You can customize
        this method for a different way of obtaining locale information.

        Returning ``None`` from this method causes the plugin to use the
        default locale.

        The return value of this method is stored in the environment dictionary
        as ``LOCALE`` key. It is then used by the plugin part of this class to
        provide translation methods to the rest of the app.
        """
        path_prefix = path.split('/')[1].lower()
        for locale in self.locales:
            if path_prefix == locale.lower():
                return locale
        return None

    @staticmethod
    def strip_prefix(path, locale):
        """
        Strip the locale prefix from the path. This static method is used to
        recalculate the request path that should be passed to Bottle. The
        return value of this method replaces the ``PATH_INFO`` key in the
        environment dictionary, and the original path is saved in
        ``ORIGINAL_PATH`` key.
        """
        return path[len(locale) + 1:]

    def set_locale(self, locale):
        """
        Store the passed in ``locale`` in a 'locale' cookie, which is used to
        override the value of the global ``default_locale``.
        """
        request.locale = locale
        response.set_cookie('locale', locale, path='/')

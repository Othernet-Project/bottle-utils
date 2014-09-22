"""
test_i18n.py: Unit tests for ``bottle_utils.i18n`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

try:
    from unittest import mock
except ImportError:
    import mock

from bottle_utils.i18n import *

MOD = 'bottle_utils.i18n.'


def is_lazy(obj):
    return hasattr(obj, '_eval')


def test_dummy_gettext():
    _ = dummy_gettext
    assert _('foo') == 'foo', "Should parrot 'foo'"
    assert _('bar') == 'bar', "Should parrot 'bar'"


def test_dummy_ngettext():
    _ = dummy_ngettext
    assert _('foo', 'foos', 1) == 'foo', "Should return 'foo'"
    assert _('foo', 'foos', 2) == 'foos', "Should return 'foos'"


def test_dummy_pgettext():
    assert dummy_pgettext('foo', 'bar') == 'bar'


def test_dummy_npgettext():
    assert dummy_npgettext('foo', 'bar', 'baz', 1) == 'bar'
    assert dummy_npgettext('foo', 'bar', 'baz', 2) == 'baz'


def test_lazy_gettext():
    _ = lazy_gettext
    s = _('foo')
    assert is_lazy(s), "Should be a lazy object"


def test_gettext_string():
    _ = lazy_ngettext
    s = _('foo', 'foos', 1)
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
def test_lazy_gettext_request(request):
    _ = lazy_gettext
    s = _('foo')
    s = s._eval()
    assert s == request.gettext.gettext.return_value, "Should use gettext"


@mock.patch(MOD + 'request')
def test_lazy_ngettext_request(request):
    _ = lazy_ngettext
    s = _('singular', 'plural', 1)
    s = s._eval()
    assert s == request.gettext.ngettext.return_value, "Should use ngettext"


@mock.patch(MOD + 'lazy_gettext')
def test_lazy_pgettext(lazy_gettext):
    ret = lazy_pgettext('foo', 'bar')
    lazy_gettext.assert_called_once_with(
        '%s%s%s' % ('foo', CONTEXT_SEPARATOR, 'bar'))
    assert ret == lazy_gettext.return_value


@mock.patch(MOD + 'lazy_ngettext')
def test_lazy_npgettext(lazy_ngettext):
    ret = lazy_npgettext('foo', 'bar', 'baz', 1)
    lazy_ngettext.assert_called_once_with(
        '%s%s%s' % ('foo', CONTEXT_SEPARATOR, 'bar'),
        '%s%s%s' % ('foo', CONTEXT_SEPARATOR, 'baz'),
        1)
    assert ret == lazy_ngettext.return_value


@mock.patch(MOD + 'request')
def test_full_path(request):
    request.fullpath = '/'
    request.query_string = ''
    s = full_path()
    assert s == '/', "Should return '/', got '%s'" % s
    request.fullpath = '/foo/bar'
    request.query_string = ''
    s = full_path()
    assert s == '/foo/bar', "Should return '/foo/bar', got '%s'" % s
    request.fullpath = '/foo/bar'
    request.query_string = 'foo=bar'
    s = full_path()
    assert s == '/foo/bar?foo=bar', "Should return everything, got '%s'" % s


def test_i18n_returns_lazy():
    s = i18n_path('/foo', 'en_US')
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
def test_i18n_path(request):
    request.locale = 'en_US'
    s = i18n_path('/foo')
    assert s == '/en_us/foo'
    request.locale = 'es_ES'
    s = i18n_path('/foo')
    assert s == '/es_es/foo'


@mock.patch(MOD + 'request')
def test_i18n_custom_locale(request):
    request.locale = 'en_US'
    s = i18n_path('/foo', locale='es_es')
    assert s == '/es_es/foo', "Should return specified locale instead"


@mock.patch(MOD + 'request')
def test_i18n_current_path(request):
    request.fullpath = '/foo/bar/baz'
    request.query_string = 'foo=bar'
    s = i18n_path(locale='en_US')
    assert s == '/en_us/foo/bar/baz?foo=bar', "Should return localized path"


def test_api_version():
    assert I18NPlugin.api == 2, "Should be version 2"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_attrs(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent')
    assert ret.app == app, "Should have app attribute"
    assert ret.langs == langs, "Should have langs attribute"
    assert ret.locales == ['foo'], "Should have locales attribute"
    assert ret.default_locale == 'foo', "Should have default_locale attr"
    assert ret.domain == 'messages', "Should have default domain"
    assert 'foo' in ret.gettext_apis, "Should have gettext API for locale"

    tret = translation.return_value
    assert ret.gettext_apis['foo'] == tret, "Translation API for locale"

@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_update_template_basics(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    I18NPlugin(app, langs, default_locale='foo', locale_dir='nonexistent')
    BaseTemplate.defaults.update.assert_called_once_with({
        '_': lazy_gettext,
        'gettext': lazy_gettext,
        'ngettext': lazy_ngettext,
        'i18n_path': i18n_path,
        'languages': langs,
    })


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_install_plugin(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent')
    app.install.assert_called_once_with(ret)


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_no_plugin(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent', noplugin=True)
    assert app.install.called == False, "Should not install the plugin"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
@mock.patch(MOD + 'warn')
def test_initialization_wanrn(warn, BaseTemplate, translation):
    def raise_os_error(*args, **kwargs):
        raise OSError('lamma crapped itself')
    translation.side_effect = raise_os_error
    app = mock.Mock()
    langs = [('foo', 'bar'), ('bar', 'baz')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent', noplugin=True)
    wcc = warn.call_count
    assert wcc == 2, "Should be called 2 times, got %s" % wcc

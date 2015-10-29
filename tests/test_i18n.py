"""
test_i18n.py: Unit tests for ``bottle_utils.i18n`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

import mock

import bottle_utils.i18n as mod

MOD = 'bottle_utils.i18n.'


def is_lazy(obj):
    return hasattr(obj, '_eval')


def test_dummy_gettext():
    _ = mod.dummy_gettext
    assert _('foo') == 'foo', "Should parrot 'foo'"
    assert _('bar') == 'bar', "Should parrot 'bar'"


def test_dummy_ngettext():
    _ = mod.dummy_ngettext
    assert _('foo', 'foos', 1) == 'foo', "Should return 'foo'"
    assert _('foo', 'foos', 2) == 'foos', "Should return 'foos'"


def test_dummy_pgettext():
    assert mod.dummy_pgettext('foo', 'bar') == 'bar'


def test_dummy_npgettext():
    assert mod.dummy_npgettext('foo', 'bar', 'baz', 1) == 'bar'
    assert mod.dummy_npgettext('foo', 'bar', 'baz', 2) == 'baz'


def test_lazy_gettext():
    _ = mod.lazy_gettext
    s = _('foo')
    assert is_lazy(s), "Should be a lazy object"


def test_gettext_string():
    _ = mod.lazy_ngettext
    s = _('foo', 'foos', 1)
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'to_unicode')
def test_lazy_gettext_request(to_unicode, req):
    _ = mod.lazy_gettext
    s = _('foo')
    s = s._eval()
    to_unicode.assert_called_once_with(req.gettext.gettext.return_value)
    assert s == to_unicode.return_value


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'to_unicode')
def test_lazy_ngettext_request(to_unicode, req):
    _ = mod.lazy_ngettext
    s = _('singular', 'plural', 1)
    s = s._eval()
    to_unicode.assert_called_once_with(req.gettext.ngettext.return_value)
    assert s == to_unicode.return_value


@mock.patch(MOD + 'lazy_gettext')
def test_lazy_pgettext(lazy_gettext):
    ret = mod.lazy_pgettext('foo', 'bar')
    lazy_gettext.assert_called_once_with(
        '%s%s%s' % ('foo', mod.CONTEXT_SEPARATOR, 'bar'))
    assert ret == lazy_gettext.return_value


@mock.patch(MOD + 'lazy_ngettext')
def test_lazy_npgettext(lazy_ngettext):
    ret = mod.lazy_npgettext('foo', 'bar', 'baz', 1)
    lazy_ngettext.assert_called_once_with(
        '%s%s%s' % ('foo', mod.CONTEXT_SEPARATOR, 'bar'),
        '%s%s%s' % ('foo', mod.CONTEXT_SEPARATOR, 'baz'),
        1)
    assert ret == lazy_ngettext.return_value


@mock.patch(MOD + 'request')
def test_full_path(req):
    req.fullpath = '/'
    req.query_string = ''
    s = mod.full_path()
    assert s == '/', "Should return '/', got '%s'" % s
    req.fullpath = '/foo/bar'
    req.query_string = ''
    s = mod.full_path()
    assert s == '/foo/bar', "Should return '/foo/bar', got '%s'" % s
    req.fullpath = '/foo/bar'
    req.query_string = 'foo=bar'
    s = mod.full_path()
    assert s == '/foo/bar?foo=bar', "Should return everything, got '%s'" % s


def test_i18n_returns_lazy():
    s = mod.i18n_path('/foo', 'en_US')
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
def test_i18n_path(req):
    req.locale = 'en_US'
    s = mod.i18n_path('/foo')
    assert s == '/en_US/foo'
    req.locale = 'es_ES'
    s = mod.i18n_path('/foo')
    assert s == '/es_ES/foo'


@mock.patch(MOD + 'request')
def test_i18n_custom_locale(req):
    req.locale = 'en_US'
    s = mod.i18n_path('/foo', locale='es_ES')
    assert s == '/es_ES/foo', "Should return specified locale instead"


@mock.patch(MOD + 'request')
def test_i18n_current_path(req):
    req.fullpath = '/foo/bar/baz'
    req.query_string = 'foo=bar'
    s = mod.i18n_path(locale='en_US')
    assert s == '/en_US/foo/bar/baz?foo=bar', "Should return localized path"


def test_i18n_url_returns_lazy():
    s = mod.i18n_url('foo', bar=2)
    assert is_lazy(s), "Should be a lazy object"


@mock.patch.object(mod, 'quoted_url')
@mock.patch.object(mod, 'request')
@mock.patch.object(mod, 'i18n_path')
def test_i18n_path_calls_get_url(i18n_path, req, quoted_url):
    s = mod.i18n_url('foo', bar=2)
    s._eval()
    quoted_url.assert_called_once_with('foo', bar=2)


@mock.patch.object(mod, 'quoted_url')
@mock.patch.object(mod, 'request')
def test_i18n_url_prefixes_get_url_results(req, quoted_url):
    quoted_url.return_value = '/foo/2/'
    req.locale = 'en'
    s = mod.i18n_url('foo', bar=2)
    assert s == '/en/foo/2/'


@mock.patch.object(mod, 'quoted_url')
@mock.patch.object(mod, 'request')
def test_i18n_url_locale_override(req, quoted_url):
    quoted_url.return_value = '/foo/2/'
    req.locale = 'en'
    s = mod.i18n_url('foo', bar=2, locale='es')
    assert s == '/es/foo/2/'


def test_api_version():
    assert mod.I18NPlugin.api == 2, "Should be version 2"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_attrs(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = mod.I18NPlugin(app, langs, default_locale='foo',
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
    mod.I18NPlugin(app, langs, default_locale='foo', locale_dir='nonexistent')
    BaseTemplate.defaults.update.assert_called_once_with({
        '_': mod.lazy_gettext,
        'gettext': mod.lazy_gettext,
        'ngettext': mod.lazy_ngettext,
        'pgettext': mod.lazy_pgettext,
        'npgettext': mod.lazy_npgettext,
        'i18n_path': mod.i18n_path,
        'i18n_url': mod.i18n_url,
        'languages': langs,
    })


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_install_plugin(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = mod.I18NPlugin(app, langs, default_locale='foo',
                         locale_dir='nonexistent')
    app.install.assert_called_once_with(ret)


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_no_plugin(BaseTemplate, translation):
    app = mock.Mock()
    langs = [('foo', 'bar')]
    mod.I18NPlugin(app, langs, default_locale='foo',
                   locale_dir='nonexistent', noplugin=True)
    assert not app.install.called, "Should not install the plugin"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
@mock.patch(MOD + 'warn')
def test_initialization_warn(warn, BaseTemplate, translation):
    def raise_os_error(*args, **kwargs):
        raise OSError('lamma crapped itself')
    translation.side_effect = raise_os_error
    app = mock.Mock()
    langs = [('foo', 'bar'), ('bar', 'baz')]
    mod.I18NPlugin(app, langs, default_locale='foo',
                   locale_dir='nonexistent', noplugin=True)
    wcc = warn.call_count
    assert wcc == 2, "Should be called 2 times, got %s" % wcc

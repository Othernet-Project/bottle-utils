"""
test_csrf.py: Unit tests for ``bottle_utils.csrf`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import sys

try:
    from unittest import mock
except ImportError:
    import mock

import bottle
from webtest import TestApp

from bottle_utils.csrf import *

PY2 = sys.version_info.major == 2

MOD = 'bottle_utils.csrf.'
MOCK_CONF = ('foo', 'bar', b'/foo/bar', 200)


@mock.patch(MOD + 'request')
def test_getting_config(request):
    request.app.config = {
        'csrf.secret': 'foo',
        'csrf.token_name': 'bar',
        'csrf.path': '/foo/bar',
        'csrf.expires': '200'
    }
    secret, name, path, expires = get_conf()
    assert secret == 'foo'
    assert name == 'bar'
    assert path == b'/foo/bar'
    assert expires == 200


@mock.patch(MOD + 'request')
def test_getting_defaults(request):
    request.app.config = {'csrf.secret': 'foo'}
    secret, name, path, expires = get_conf()
    assert secret == 'foo'
    assert name == '_csrf_token'
    assert path == b'/'
    assert expires == 600


@mock.patch(MOD + 'request')
def test_getting_config_fails_with_no_secret(request):
    request.app.config = {}
    try:
        secret, name, path, expires = get_conf()
    except KeyError:
        assert True
        return
    assert False, "KeyError was not raised"


@mock.patch(MOD + 'request')
def test_expires_defaults_if_non_numeric(request):
    request.app.config = {
        'csrf.secret': 'foo',
        'csrf.expires': 'abc'
    }
    _, _, _, expires = get_conf()
    assert expires == 600


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'hashlib')
@mock.patch(MOD + 'os')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_generate_token(request, response, os, hashlib, get_conf):
    get_conf.return_value = MOCK_CONF
    hashlib.sha256.return_value.hexdigest.return_value = 'abc'
    generate_csrf_token()
    response.set_cookie.assert_called_once_with('bar', b'abc',
                                                path=b'/foo/bar',
                                                secret='foo', max_age=200)
    assert request.csrf_token == 'abc'


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'generate_csrf_token')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_new_csrf_token(request, response, generate_csrf_token, get_conf):
    get_conf.return_value = ('foo', 'bar', b'/foo/bar', 200)
    request.get_cookie.return_value = None
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_token(handler)
    handler()
    assert generate_csrf_token.called


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'generate_csrf_token')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_old_csrf_token(request, response, generate_csrf_token, get_conf):
    get_conf.return_value = MOCK_CONF
    request.get_cookie.return_value = b'abc'
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_token(handler)
    handler()
    assert not generate_csrf_token.called
    assert request.csrf_token == 'abc'
    response.set_cookie.assert_called_once_with(mock.ANY, b'abc',
                                                path=mock.ANY,
                                                secret=mock.ANY,
                                                max_age=mock.ANY)

@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'generate_csrf_token')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_cache_header(request, response, generate_csrf_token, get_conf):
    get_conf.return_value = MOCK_CONF
    response.headers = {}
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_token(handler)
    handler()
    assert 'Cache-Control' in response.headers
    assert response.headers['Cache-Control'] == (
        'no-cache, max-age=0, must-revalidate, no-store')


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'request')
@mock.patch(MOD + 'abort')
def test_protect_no_token(abort, request, get_conf):
    get_conf.return_value = MOCK_CONF
    request.get_cookie.return_value = None
    abort.side_effect = bottle.HTTPResponse
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_protect(handler)
    try:
        handler()
        assert False, 'Should have raised HTTPResponse'
    except bottle.HTTPResponse:
        pass
    abort.assert_called_once_with(403, mock.ANY)


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
@mock.patch(MOD + 'abort')
def test_protect_no_form_token(abort, request, response, get_conf):
    get_conf.return_value = MOCK_CONF
    request.get_cookie.return_value = b'abc'
    request.forms.get.return_value = None
    abort.side_effect = bottle.HTTPResponse
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_protect(handler)
    try:
        handler()
        assert False, 'Should have raised HTTPResponse'
    except bottle.HTTPResponse:
        pass
    response.delete_cookie.assert_called_once_with(MOCK_CONF[1], path=mock.ANY,
                                                   secret=mock.ANY,
                                                   max_age=mock.ANY)
    abort.assert_called_once_with(403, mock.ANY)


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
@mock.patch(MOD + 'abort')
def test_protect_token_mismatch(abort, request, response, get_conf):
    get_conf.return_value = MOCK_CONF
    request.get_cookie.return_value = b'abc'
    request.forms.get.return_value = b'abd'
    abort.side_effect = bottle.HTTPResponse
    handler = mock.Mock()
    handler.__name__ = str('foo')
    handler = csrf_protect(handler)
    try:
        handler()
        assert False, 'Should have raised HTTPResponse'
    except bottle.HTTPResponse:
        pass
    response.delete_cookie.assert_called_once_with(MOCK_CONF[1], path=mock.ANY,
                                                   secret=mock.ANY,
                                                   max_age=mock.ANY)
    abort.assert_called_once_with(403, mock.ANY)


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'generate_csrf_token')
@mock.patch(MOD + 'request')
def test_protect_good_token(request, generate_csrf_token, get_conf):
    get_conf.return_value = MOCK_CONF
    request.get_cookie.return_value = b'abc'
    request.forms.get.return_value = b'abc'
    func = mock.Mock()
    func.__name__ = str('foo')
    handler = csrf_protect(func)
    handler()
    assert generate_csrf_token.called
    assert func.called


@mock.patch(MOD + 'get_conf')
@mock.patch(MOD + 'request')
def test_csrf_tag(request, get_conf):
    get_conf.return_value = MOCK_CONF
    request.csrf_token = 'abc'
    s = csrf_tag()
    assert s.startswith('<input') and s.endswith('>')
    assert 'value="abc"' in s
    assert 'name="bar"' in s
    assert 'type="hidden"' in s

# Integration tests

from csrf_app import test_app


def test_csrf_token():
    res = test_app.get('/csrf_token')
    assert '_csrf_token' in test_app.cookies
    token = test_app.cookies['_csrf_token']
    if PY2:
        res = res.form.submit()
    else:
        # We need to manually set the cookie because WebTest doesn't do it for
        # us...
        form_token = res.form['_csrf_token'].value
        res = test_app.post(
            '/csrf_token', {'_csrf_token': form_token},
            headers=(('Cookie', '_csrf_token=%s;' % token),))
    assert res.status == '200 OK'
    assert res.text == 'success'
    # New token is set
    assert test_app.cookies['_csrf_token'] != token


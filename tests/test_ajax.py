"""
test_ajax.py: Unit tests for ``bottle_utils.ajax`` module

Bottle Utils
2014-2015 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

try:
    from unittest import mock
except ImportError:
    import mock

import bottle
import bottle_utils.ajax as mod

MOD = 'bottle_utils.ajax.'


def mock_handler(**kwargs):
    handler = mock.Mock()
    handler.__name__ = str('handler')
    handler.return_value = kwargs
    return handler


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'abort')
def test_ajax_only_aborts_non_ajax(abort, request):
    handler = mock_handler()
    ajax_handler = mod.ajax_only(handler)
    request.is_xhr = True
    ajax_handler()
    assert not abort.called
    request.is_xhr = False
    ajax_handler()
    abort.assert_called_with(400)


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'template')
def test_roca_as_view_deco(template, request):
    handler = mock_handler()
    roca_handler = mod.roca_view('foo', 'bar')(handler)
    request.is_xhr = False
    roca_handler()
    template.assert_called_once_with('foo')


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'template')
def test_roca_as_view_deco_xhr(template, request):
    handler = mock_handler()
    roca_handler = mod.roca_view('foo', 'bar')(handler)
    request.is_xhr = True
    roca_handler()
    template.assert_called_once_with('bar')


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'template')
def test_roca_with_defaults(template, request):
    handler =  mock_handler()
    roca_handler = mod.roca_view('foo', 'bar', foo='bar')(handler)
    request.is_xhr = False
    roca_handler()
    template.assert_called_once_with('foo', foo='bar')


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'template')
def test_roca_with_defaults_merged(template, request):
    handler =  mock_handler(bar='baz')
    roca_handler = mod.roca_view('foo', 'bar', foo='bar')(handler)
    request.is_xhr = False
    roca_handler()
    template.assert_called_once_with('foo', foo='bar', bar='baz')


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'template')
def test_roca_custom_template_func(template, request):
    handler = mock_handler()
    faux_tpl = mock.Mock()
    roca_handler = mod.roca_view('foo', 'bar', template_func=faux_tpl)(handler)
    roca_handler()
    assert faux_tpl.called
    assert not template.called


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'template')
def test_cache_header_roca(template, response, request):
    response.headers = bottle.HeaderDict()
    handler = mock_handler()
    faux_tpl = mock.Mock()
    roca_handler = mod.roca_view('foo', 'bar', template_func=faux_tpl)(handler)
    roca_handler()
    assert response.headers['Cache-Control'] == 'no-store'


# Integration tests

from app import test_app


def test_normal_request_returns_400():
    res = test_app.get('/ajax_only', expect_errors=True)
    assert res.status_int == 400


def test_ajax_request_does_work():
    res = test_app.get('/ajax_only', xhr=True)
    assert res.status == '200 OK'
    assert res.ubody == 'success'

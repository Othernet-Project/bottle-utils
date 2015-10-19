"""
test_ajax.py: Unit tests for ``bottle_utils.ajax`` module

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

from bottle_utils.flash import *

PY2 = sys.version_info.major == 2
MOD = 'bottle_utils.flash.'
FAKE_DECOR = lambda fn: fn


@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_get_message(request, response):
    request._message = 'foo'
    ret = get_message() # get_message is a lazy function
    assert str(ret) == 'foo'
    response.delete_cookie.assert_called_once_with(MESSAGE_KEY, path=ROOT,
                                                   secret=SECRET)


@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_set_message(request, response):
    set_message('foo')
    response.set_cookie.assert_called_once_with(MESSAGE_KEY, str('foo'),
                                                path=ROOT, secret=SECRET)
    assert request._message == 'foo'


@mock.patch(MOD + 'get_message')
@mock.patch(MOD + 'response')
@mock.patch(MOD + 'request')
def test_plugin(request, response, get_message):
    fn = mock.Mock()
    fn.__name__ = str('foo')
    wrapped = message_plugin(fn)
    ret = wrapped()
    request.get_cookie.assert_called_once_with(MESSAGE_KEY, str(),
                                               secret=SECRET)
    cookie = request.get_cookie.return_value
    if PY2:
        assert request._message == cookie.decode.return_value
    else:
        assert request._message == cookie
    assert request.message == get_message.return_value
    assert response.flash == set_message
    assert ret == fn.return_value


# Integration tests

from flash_app import test_app


def test_getting_empty_message():
    res = test_app.get('/message')
    assert res.ubody == ''


def test_setting_and_getting_message():
    res = test_app.post('/message')
    if PY2:
        res = test_app.get('/message')
    else:
        msg = test_app.cookies['_flash']
        res = test_app.get(
            '/message', headers=(('Cookie', '_flash=%s;' % msg),))
    assert res.ubody == 'Come on!'


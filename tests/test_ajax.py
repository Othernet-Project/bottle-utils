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

import bottle
from webtest import TestApp

from bottle_utils.ajax import *

PY2 = sys.version_info.major == 2


# Test handler
@bottle.get('/')
@ajax_only
def ajax_only_handler():
    return 'success'

# Test app
app = TestApp(bottle.default_app())

MOD = 'bottle_utils.ajax.'


@mock.patch(MOD + 'request')
@mock.patch(MOD + 'abort')
def test_ajax_only_aborts_non_ajax(abort, request):
    handler = mock.Mock()
    handler.__name__ = str('handler')
    ajax_handler = ajax_only(handler)
    request.is_xhr = True
    ajax_handler()
    assert not abort.called
    request.is_xhr = False
    ajax_handler()
    abort.assert_called_with(400)


def test_normal_request_returns_400():
    res = app.get('/', expect_errors=True)
    assert res.status_int == 400


def test_ajax_request_deos_work():
    res = app.get('/', xhr=True)
    assert res.status == '200 OK'
    assert res.ubody == 'success'

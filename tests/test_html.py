# -*- coding: utf-8 -*-
"""
test_html.py: Unit tests for ``bottle_utils.html`` module

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

from bottle import FormsDict

from bottle_utils.html import *


MOD = 'bottle_utils.html.'


def assert_attr(s, name, val):
    assert ('%s="%s"' % (name, val)) in s


def assert_value(s, val):
    assert_attr(s, 'value', val)


def assert_type(s, val):
    assert_attr(s, 'type', val)


def assert_name(s, val):
    assert_attr(s, 'name', val)


def assert_tag(s, name):
    assert s.startswith('<' + name) and s.endswith('>')


def assert_content(s, content):
    assert ('>%s<' % content) in s


def test_plur():
    assert plur('book', 1) == 'book'
    assert plur('book', 2) == 'books'


def test_custom_plural_function():
    pfunc = lambda n: n > 2
    assert plur('book', 1, pfunc) == 'book'
    assert plur('book', 2, pfunc) == 'book'
    assert plur('book', 3, pfunc) == 'books'


def test_custom_convert_function():
    cfunc = lambda s, p: s + 'mi' if p else s
    assert plur('book', 1, convert=cfunc) == 'book'
    assert plur('book', 2, convert=cfunc) == 'bookmi'


def test_hsize():
    assert hsize(12) == '12.00 B'
    assert hsize(1030) == '1.01 KB'
    assert hsize(2097152) == '2.00 MB'


def test_hsize_step():
    assert hsize(12, step=1000) == '12.00 B'
    assert hsize(1200, step=1000) == '1.20 KB'


def test_hsize_units():
    assert hsize(12, 'm', 1000) == '12.00 m'
    assert hsize(1200, 'm', 1000) == '1.20 Km'


def test_attr():
    assert attr('foo', 'bar') == 'foo="bar"'
    assert attr('foo', 1) == 'foo="1"'


def test_tag():
    assert tag('foo') == '<foo></foo>'


def test_tag_content():
    assert tag('foo', 'bar') == '<foo>bar</foo>'


def test_tag_content_html():
    assert tag('foo', '<bar>') == '<foo><bar></foo>'


def test_nonclosing_tag():
    assert tag('foo', nonclosing=True) == '<foo>'
    assert tag('foo', 'bar', nonclosing=True) == '<foo>'


def test_tag_attributes():
    assert tag('foo', bar='fam') == '<foo bar="fam"></foo>'


def test_tag_attribute_with_underscore():
    assert tag('foo', _bar='fam') == '<foo bar="fam"></foo>'


def test_hidden_field():
    s = HIDDEN('foo', 'bar')
    # Making partial assumptions because attribute order is not always same
    assert_tag(s, 'input')
    assert_type(s, 'hidden')
    assert_name(s, 'foo')
    assert_value(s, 'bar')


def test_vinput():
    s = vinput('foo', {})
    assert_tag(s, 'input')
    assert_name(s, 'foo')
    assert_attr(s, 'id', 'foo')


def test_vinput_override_id():
    s = vinput('foo', {}, _id='bar')
    assert_attr(s, 'id', 'bar')


def test_vinput_value():
    s = vinput('foo', {'foo': '12'})
    assert_value(s, '12')


def test_varea():
    s = varea('foo', {})
    assert_tag(s, 'textarea')
    assert_name(s, 'foo')
    assert_attr(s, 'id', 'foo')


def test_varea_override_id():
    s = varea('foo', {}, _id='bar')


def test_varea_value():
    s = varea('foo', {'foo': 'bar'})
    assert_content(s, 'bar')


def test_vcheckbox():
    s = vcheckbox('foo', 'fooval', {})
    assert_tag(s, 'input')
    assert_type(s, 'checkbox')
    assert_value(s, 'fooval')
    assert_attr(s, 'id', 'foo')


def test_vcheckbox_value():
    s = vcheckbox('foo', 'fooval', {'foo': 'fooval'})
    assert 'checked' in s


def test_vcheckbox_value_with_string_coertion():
    s = vcheckbox('foo', 1, {'foo': '1'})
    assert 'checked' in s


def test_vcheckbox_value_no_partial_match():
    s = vcheckbox('foo', 'fooval', {'foo': 'foovaliant'})
    assert 'checked' not in s


def test_vcheckbox_values_list():
    s = vcheckbox('foo', 'fooval', {'foo': ['fooval', 'barval']})
    assert 'checked' in s


def test_vcheckbox_default():
    s = vcheckbox('foo', 'fooval', {}, True)
    assert 'checked' in s
    s = vcheckbox('foo', 'fooval', {}, False)
    assert 'checked' not in s


def test_vselect():
    s = vselect('foo', [], {})
    assert_tag(s, 'select')
    assert_content(s, '')


def test_vselect_choices():
    s = vselect('foo', ((1, 'bar'), (2, 'baz')), {})
    assert tag('option', 'bar', value=1) in s
    assert tag('option', 'baz', value=2) in s


def test_vselect_value():
    # FIXME: This test may fail in Python 3.4 because of HTML attribute
    # ordering.
    s = vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 1})
    assert tag('option', 'bar', value=1, selected=None) in s
    assert tag('option', 'baz', value=2) in s

    s = vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 2})
    assert tag('option', 'bar', value=1) in s
    assert tag('option', 'baz', value=2, selected=None) in s


def test_vselect_value_with_unicode_coertion():
    # FIXME: This test may fail in Python 3.4 because of HTML attribute
    # ordering.
    s = vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': '1'})
    assert tag('option', 'bar', value=1, selected=None) in s
    assert tag('option', 'baz', value=2) in s

    s = vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 2})
    assert tag('option', 'bar', value=1) in s
    assert tag('option', 'baz', value=2, selected=None) in s


def test_vselect_empty():
    s = vselect('foo', ((1, 'bar'),), {}, empty='foo')
    assert tag('option', 'foo', value=None) in s
    assert tag('option', 'bar', value=1) in s


def test_form_tag_default():
    assert form() == '<form>'


def test_form_tag_method():
    assert form('POST') == '<form method="POST">'
    assert form('GET') == '<form method="GET">'


def test_form_tag_faux_method():
    assert '<form method="POST">' in form('PUT')
    assert HIDDEN('_method', 'PUT') in form('PUT')


def test_form_action():
    assert form(action='/foo') == '<form action="/foo">'


@mock.patch('bottle_utils.csrf.csrf_tag')
def test_form_csrf(csrf_tag):
    csrf_tag.return_value = 'foo'
    assert 'foo' in form(csrf=True)


def test_form_multipart():
    assert form(multipart=True) == '<form enctype="multipart/form-data">'


def test_form_other_attrs():
    assert form(_id='foo') == '<form id="foo">'


def test_link_other():
    s = link_other('foo', '/bar', '/baz')
    assert_tag(s, 'a')
    assert_attr(s, 'href', '/bar')
    s = link_other('foo', '/bar', '/bar')
    assert s == '<span>foo</span>'


def test_link_other_alternative_wrapper():
    s = link_other('foo', '/bar', '/bar', SPAN)
    assert_tag(s, 'span')
    assert_content(s, 'foo')


def test_link_other_common_kwargs():
    s = link_other('foo', '/bar', '/baz', SPAN, _class='cls')
    assert_attr(s, 'class', 'cls')
    s = link_other('foo', '/bar', '/bar', SPAN, _class='cls')
    assert_attr(s, 'class', 'cls')


def test_trunc():
    assert trunc('123456789', 10) == '123456789'
    assert trunc('123456789', 4) == '1234...'


def test_yesno():
    assert yesno(True) == 'yes'
    assert yesno(False) == 'no'


def test_yesno_custom_yes_no():
    assert yesno(True, 'available', 'not available') == 'available'
    assert yesno(False, 'available', 'not available') == 'not available'


@mock.patch(MOD + 'request')
def test_to_qs(request):
    request.path = '/'
    query = FormsDict([('a', '1'), ('b', '3')])
    ret = to_qs(query)
    assert 'a=1' in ret
    assert 'b=3' in ret


@mock.patch(MOD + 'request')
def test_to_qs_dict(request):
    request.path = '/'
    query = {'a': '1', 'b': '3'}
    ret = to_qs(query)
    assert 'a=1' in ret
    assert 'b=3' in ret


@mock.patch(MOD + 'request')
def test_to_qs_unicode(request):
    request.path = '/'
    query = {'a': 'јуникод'}
    assert to_qs(query) == '/?a=%D1%98%D1%83%D0%BD%D0%B8%D0%BA%D0%BE%D0%B4'


@mock.patch(MOD + 'request')
def test_add_qparam(request):
    request.path = '/'
    request.query = FormsDict([('a', '1'), ('b', '3'), ('c', '4')])
    ret = add_qparam('a', '0')
    assert 'a=0' in ret
    assert 'a=1' in ret


@mock.patch(MOD + 'request')
def test_add_qparam_unicode_coercion(request):
    request.path = '/'
    request.query = FormsDict([('a', '1'), ('b', '3'), ('c', '4')])
    ret = add_qparam('a', 0)
    assert 'a=0' in ret
    assert 'a=1' in ret


@mock.patch(MOD + 'request')
def test_set_qparam(request):
    request.path = '/'
    request.query = FormsDict([('a', '1'), ('b', '3'), ('c', '4')])
    ret = set_qparam('a', '0')
    assert 'a=0' in ret
    assert 'a=1' not in ret


@mock.patch(MOD + 'request')
def test_set_qparam_unicode_coercion(request):
    request.path = '/'
    request.query = FormsDict([('a', '1'), ('b', '3'), ('c', '4')])
    ret = set_qparam('a', 0)
    assert 'a=0' in ret
    assert 'a=1' not in ret


@mock.patch(MOD + 'request')
def test_del_qparam(request):
    request.path = '/'
    request.query = FormsDict([('a', '1'), ('b', '3'), ('c', '4')])
    ret = set_qparam('a', '0')
    assert 'a=1' not in ret


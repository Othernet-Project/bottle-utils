# -*- coding: utf-8 -*-

"""
test_html.py: Unit tests for ``bottle_utils.html`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import mock
import pytest

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import bottle_utils.html as mod


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
    assert mod.plur('book', 1) == 'book'
    assert mod.plur('book', 2) == 'books'


def test_custom_plural_function():
    pfunc = lambda n: n > 2
    assert mod.plur('book', 1, pfunc) == 'book'
    assert mod.plur('book', 2, pfunc) == 'book'
    assert mod.plur('book', 3, pfunc) == 'books'


def test_custom_convert_function():
    cfunc = lambda s, p: s + 'mi' if p else s
    assert mod.plur('book', 1, convert=cfunc) == 'book'
    assert mod.plur('book', 2, convert=cfunc) == 'bookmi'


def test_hsize():
    assert mod.hsize(12) == '12.00 B'
    assert mod.hsize(1030) == '1.01 KB'
    assert mod.hsize(2097152) == '2.00 MB'
    assert mod.hsize(12, sep='') == '12.00B'
    assert mod.hsize(12, rounding=0) == '12 B'


def test_hsize_step():
    assert mod.hsize(12, step=1000) == '12.00 B'
    assert mod.hsize(1200, step=1000) == '1.20 KB'


def test_hsize_units():
    assert mod.hsize(12, 'm', 1000) == '12.00 m'
    assert mod.hsize(1200, 'm', 1000) == '1.20 Km'


def test_attr():
    assert mod.attr('foo', 'bar') == 'foo="bar"'
    assert mod.attr('foo', 1) == 'foo="1"'


def test_tag():
    assert mod.tag('foo') == '<foo></foo>'


def test_tag_content():
    assert mod.tag('foo', 'bar') == '<foo>bar</foo>'


def test_tag_content_html():
    assert mod.tag('foo', '<bar>') == '<foo><bar></foo>'


def test_nonclosing_tag():
    assert mod.tag('foo', nonclosing=True) == '<foo>'
    assert mod.tag('foo', 'bar', nonclosing=True) == '<foo>'


def test_tag_attributes():
    assert mod.tag('foo', bar='fam') == '<foo bar="fam"></foo>'


def test_tag_attribute_with_underscore():
    assert mod.tag('foo', _bar='fam') == '<foo bar="fam"></foo>'


def test_hidden_field():
    s = mod.HIDDEN('foo', 'bar')
    # Making partial assumptions because attribute order is not always same
    assert_tag(s, 'input')
    assert_type(s, 'hidden')
    assert_name(s, 'foo')
    assert_value(s, 'bar')


def test_vinput():
    s = mod.vinput('foo', {})
    assert_tag(s, 'input')
    assert_name(s, 'foo')
    assert_attr(s, 'id', 'foo')


def test_vinput_override_id():
    s = mod.vinput('foo', {}, _id='bar')
    assert_attr(s, 'id', 'bar')


def test_vinput_value():
    s = mod.vinput('foo', {'foo': '12'})
    assert_value(s, '12')


def test_varea():
    s = mod.varea('foo', {})
    assert_tag(s, 'textarea')
    assert_name(s, 'foo')
    assert_attr(s, 'id', 'foo')


def test_varea_override_id():
    s = mod.varea('foo', {}, _id='bar')
    assert_attr(s, 'id', 'bar')


def test_varea_value():
    s = mod.varea('foo', {'foo': 'bar'})
    assert_content(s, 'bar')


def test_vcheckbox():
    s = mod.vcheckbox('foo', 'fooval', {})
    assert_tag(s, 'input')
    assert_type(s, 'checkbox')
    assert_value(s, 'fooval')
    assert_attr(s, 'id', 'foo')


def test_vcheckbox_value():
    s = mod.vcheckbox('foo', 'fooval', {'foo': 'fooval'})
    assert 'checked' in s


def test_vcheckbox_value_with_string_coertion():
    s = mod.vcheckbox('foo', 1, {'foo': '1'})
    assert 'checked' in s


def test_vcheckbox_value_no_partial_match():
    s = mod.vcheckbox('foo', 'fooval', {'foo': 'foovaliant'})
    assert 'checked' not in s


def test_vcheckbox_values_list():
    s = mod.vcheckbox('foo', 'fooval', {'foo': ['fooval', 'barval']})
    assert 'checked' in s


def test_vcheckbox_default():
    s = mod.vcheckbox('foo', 'fooval', {}, True)
    assert 'checked' in s
    s = mod.vcheckbox('foo', 'fooval', {}, False)
    assert 'checked' not in s


def test_vselect():
    s = mod.vselect('foo', [], {})
    assert_tag(s, 'select')
    assert_content(s, '')


def test_vselect_choices():
    s = mod.vselect('foo', ((1, 'bar'), (2, 'baz')), {})
    assert mod.tag('option', 'bar', value=1) in s
    assert mod.tag('option', 'baz', value=2) in s


def test_vselect_value():
    # FIXME: This test may fail in Python 3.4 because of HTML attribute
    # ordering.
    s = mod.vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 1})
    assert mod.tag('option', 'bar', value=1, selected=None) in s
    assert mod.tag('option', 'baz', value=2) in s
    s = mod.vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 2})
    assert mod.tag('option', 'bar', value=1) in s
    assert mod.tag('option', 'baz', value=2, selected=None) in s


def test_vselect_value_with_unicode_coertion():
    # FIXME: This test may fail in Python 3.4 because of HTML attribute
    # ordering.
    s = mod.vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': '1'})
    assert mod.tag('option', 'bar', value=1, selected=None) in s
    assert mod.tag('option', 'baz', value=2) in s
    s = mod.vselect('foo', ((1, 'bar'), (2, 'baz')), {'foo': 2})
    assert mod.tag('option', 'bar', value=1) in s
    assert mod.tag('option', 'baz', value=2, selected=None) in s


def test_vselect_empty():
    s = mod.vselect('foo', ((1, 'bar'),), {}, empty='foo')
    assert mod.tag('option', 'foo', value=None) in s
    assert mod.tag('option', 'bar', value=1) in s


def test_form_tag_default():
    assert mod.form() == '<form>'


def test_form_tag_method():
    assert mod.form('POST') == '<form method="POST">'
    assert mod.form('GET') == '<form method="GET">'


def test_form_tag_faux_method():
    assert '<form method="POST">' in mod.form('PUT')
    assert mod.HIDDEN('_method', 'PUT') in mod.form('PUT')


def test_form_action():
    assert mod.form(action='/foo') == '<form action="/foo">'


def test_form_multipart():
    assert mod.form(multipart=True) == '<form enctype="multipart/form-data">'


def test_form_other_attrs():
    assert mod.form(_id='foo') == '<form id="foo">'


def test_link_other():
    s = mod.link_other('foo', '/bar', '/baz')
    assert_tag(s, 'a')
    assert_attr(s, 'href', '/bar')
    s = mod.link_other('foo', '/bar', '/bar')
    assert s == '<span>foo</span>'


def test_link_other_alternative_wrapper():
    s = mod.link_other('foo', '/bar', '/bar', mod.SPAN)
    assert_tag(s, 'span')
    assert_content(s, 'foo')


def test_link_other_common_kwargs():
    s = mod.link_other('foo', '/bar', '/baz', mod.SPAN, _class='cls')
    assert_attr(s, 'class', 'cls')
    s = mod.link_other('foo', '/bar', '/bar', mod.SPAN, _class='cls')
    assert_attr(s, 'class', 'cls')


def test_trunc():
    assert mod.trunc('123456789', 10) == '123456789'
    assert mod.trunc('123456789', 4) == '1234...'


def test_yesno():
    assert mod.yesno(True) == 'yes'
    assert mod.yesno(False) == 'no'


def test_yesno_custom_yes_no():
    assert mod.yesno(True, 'available', 'not available') == 'available'
    assert mod.yesno(False, 'available', 'not available') == 'not available'


def test_query_cls_is_form_dict():
    qs = 'a=1&b=2'
    q = mod.QueryDict(qs)
    assert q['a'] == '1'
    assert q['b'] == '2'


def test_query_to_string():
    qs = 'a=1&b=2'
    q = mod.QueryDict(qs)
    # NOTE: order of keys is non-deterministic
    assert str(q) in ['a=1&b=2', 'b=2&a=1']


def test_query_empty():
    q = mod.QueryDict()
    assert str(q) == ''


def test_query_with_unicode():
    q = mod.QueryDict()
    q['a'] = 'јуникод'
    assert str(q) == 'a=%D1%98%D1%83%D0%BD%D0%B8%D0%BA%D0%BE%D0%B4'


def test_query_add():
    q = mod.QueryDict()
    q.add_qparam(a=1)
    assert str(q) == 'a=1'


def test_query_add_multiple():
    q = mod.QueryDict()
    q.add_qparam(a=1, b=2)
    assert str(q) in ['a=1&b=2', 'b=2&a=1']


def test_query_add_chaining():
    q = mod.QueryDict()
    q.add_qparam(a=1).add_qparam(b=2)
    assert str(q) in ['a=1&b=2', 'b=2&a=1']


def test_query_set():
    q = mod.QueryDict('a=1')
    q.set_qparam(a=0)
    assert str(q) == 'a=0'


def test_query_delete():
    q = mod.QueryDict('a=1&b=2')
    q.del_qparam('a')
    assert str(q) == 'b=2'


def test_query_delete_multiple():
    q = mod.QueryDict('a=1&b=2')
    q.del_qparam('a', 'b')
    assert str(q) == ''


def test_query_delete_chaining():
    q = mod.QueryDict('a=1&b=2')
    q.del_qparam('a').set_qparam(b=0)
    assert str(q) == 'b=0'


def test_query_set_multiple():
    q = mod.QueryDict('a=1&b=2')
    q.set_qparam(a=0, b=0)
    assert str(q) in ['a=0&b=0', 'b=0&a=0']


def test_query_set_chaining():
    q = mod.QueryDict('a=1')
    q.set_qparam(a=0).add_qparam(a=2)
    assert str(q) in ['a=0&a=2', 'a=2&a=0']


def test_to_qs():
    q = mod.QueryDict('a=1')
    assert q.to_qs() == '?a=1'


def test_to_qs_unicode():
    for case in (u'かわいい',
                 u'صباح الخير',
                 u'лепо',
                 u'les miserablés',
                 u'nije ćirilica'):
        q = mod.QueryDict(u'a=' + case)
        try:
            assert q.to_qs()
        except Exception as exc:
            pytest.fail("Should not raise: {0}".format(exc))


def test_qs_concat_left():
    qs = mod.QueryDict('a=0')
    assert 'foo' + qs == 'foo?a=0'


def test_qs_conact_right():
    qs = mod.QueryDict('a=0')
    assert qs + '&foo=2' == '?a=0&foo=2'


def test_add_qparam():
    qs = 'a=1&b=3&c=4'
    ret = mod.add_qparam(qs, a='0')
    assert 'a=0' in str(ret)
    assert 'a=1' in str(ret)


def test_add_qparam_unicode_coercion():
    qs = 'a=1&b=3&c=4'
    ret = mod.add_qparam(qs, a=0)
    assert 'a=0' in str(ret)
    assert 'a=1' in str(ret)


def test_add_qparam_chaining():
    qs = 'a=1&b=3&c=4'
    ret = mod.add_qparam(mod.add_qparam(qs, a=0), d=2)
    assert 'a=0' in str(ret)
    assert 'd=2' in str(ret)


@mock.patch(MOD + 'request')
def test_add_qparam_default_query_string(request):
    request.query_string = 'a=1&b=2'
    ret = mod.add_qparam(c=3)
    assert 'a=1' in str(ret)
    assert 'b=2' in str(ret)
    assert 'c=3' in str(ret)


def test_set_qparam():
    qs = 'a=1&b=3&c=4'
    ret = mod.set_qparam(qs, a='0')
    assert 'a=0' in str(ret)
    assert 'a=1' not in str(ret)


def test_set_qparam_unicode_coercion():
    qs = 'a=1&b=3&c=4'
    ret = mod.set_qparam(qs, a=0)
    assert 'a=0' in str(ret)
    assert 'a=1' not in str(ret)


def test_set_qparam_multiple():
    qs = 'a=1&b=3&c=4'
    ret = mod.set_qparam(mod.set_qparam(qs, a=2), b=4)
    assert 'a=2' in str(ret)
    assert 'a=1' not in str(ret)
    assert 'b=4' in str(ret)
    assert 'b=3' not in str(ret)


@mock.patch(MOD + 'request')
def test_set_qparam_default(request):
    request.query_string = 'a=1&b=2'
    ret = mod.set_qparam(a=2)
    assert 'a=2' in str(ret)
    assert 'b=2' in str(ret)
    assert 'a=1' not in str(ret)


def test_del_qparam():
    qs = 'a=1&b=3&c=4'
    ret = mod.del_qparam(qs, 'a')
    assert 'a=1' not in str(ret)


def test_del_all():
    qs = 'a=1&a=2&b=2'
    ret = mod.del_qparam(qs, 'a')
    assert 'a=1' not in str(ret)
    assert 'a=2' not in str(ret)
    assert 'b=2' in str(ret)


@mock.patch(MOD + 'request')
def test_del_qparam_default(request):
    request.query_string = 'a=1&b=2'
    ret = mod.del_qparam(None, 'a')
    assert 'a=1' not in str(ret)
    assert 'b=2' in str(ret)


@mock.patch(MOD + 'request')
@pytest.mark.parametrize(('parts', 'expected', 'path', 'with_scheme'), (
    ['http://outernet.is/?query', '//outernet.is', '', False],
    ['http://outernet.is/?query', 'http://outernet.is', '', True],
    ['http://outernet.is/?query', '//outernet.is/suffix', '/suffix', False],
    ['https://outernet.is/?query', '//outernet.is', '', False],
    ['https://outernet.is/?query', 'https://outernet.is', '', True],
    ['https://outernet.is/?query', '//outernet.is/suffix', '/suffix', False],
    ['http://outernet.is:80/?query', 'http://outernet.is', '', True],
    ['https://outernet.is:80/?query', '//outernet.is', '', False],
    ['https://outernet.is:80/?query', 'https://outernet.is', '', True],
    ['http://outernet.is:443/?query', 'http://outernet.is', '', True],
    ['https://outernet.is:443/?query', '//outernet.is', '', False],
    ['https://outernet.is:443/?query', 'https://outernet.is', '', True],
    ['https://outernet.is:443/?query', 'https://outernet.is/path', '/path', True],
    ['http://outernet.is:1234/?query', 'http://outernet.is:1234', '', True],
    ['https://outernet.is:1234/?query', '//outernet.is:1234', '', False],
    ['https://outernet.is:1234/?query', '//outernet.is:1234/path', '/path', False],
))
def test_full_domain(request, parts, expected, path, with_scheme):
    request.urlparts = urlparse.urlsplit(parts)
    ret = mod.full_url(path=path, with_scheme=with_scheme)
    assert ret == expected

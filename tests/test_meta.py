"""
test_meta.py: Unit tests for ``bottle_utils.meta`` module

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

from bottle_utils.meta import *

PY2 = sys.version_info.major == 2
MOD = 'bottle_utils.meta.'


@mock.patch.object(MetaBase, 'render')
def test_meta_base_str_calls_render(render):
    m = MetaBase()
    render.return_value = 'foo'
    assert str(m) == 'foo'
    assert render.called


def test_simple_meta():
    expected = '<meta foo="bar" content="baz">'
    assert SimpleMetadata.meta('foo', 'bar', 'baz') == expected


def test_simple():
    m = SimpleMetadata()
    assert str(m) == ''


def test_simple_title():
    m = SimpleMetadata(title='foo')
    s = m.render()
    assert '<title>foo</title>' in s


@mock.patch.object(SimpleMetadata, 'simple')
def test_simple_description(simple):
    m = SimpleMetadata(description='foo')
    m.render()
    simple.assert_called_once_with('description', 'foo')


@mock.patch(MOD + 'Metadata.meta')
def test_metadata_prop(meta):
    m = Metadata()
    ret = m.prop('foo', 'bar', 'baz')
    assert ret == meta.return_value
    meta.assert_called_once_with('property', 'foo:bar', 'baz')


@mock.patch(MOD + 'Metadata.meta')
def test_metadata_simple(meta):
    m = Metadata()
    ret = m.simple('foo', 'bar')
    assert ret == meta.return_value
    meta.assert_called_once_with('name', 'foo', 'bar')


@mock.patch(MOD + 'Metadata.meta')
def test_metadata_nameprop(meta):
    m = Metadata()
    ret = m.nameprop('foo', 'bar', 'baz')
    assert ret == meta.return_value
    meta.assert_called_once_with('name', 'foo:bar', 'baz')


@mock.patch(MOD + 'Metadata.meta')
def test_metadata_itemprop(meta):
    m = Metadata()
    ret = m.itemprop('foo', 'bar')
    assert ret == meta.return_value
    meta.assert_called_once_with('itemprop', 'foo', 'bar')


@mock.patch.object(Metadata, 'nameprop')
def test_metadata_twitterprop(nameprop):
    m = Metadata()
    ret = m.twitterprop('foo', 'bar')
    assert ret == nameprop.return_value
    nameprop.assert_called_once_with('twitter', 'foo', 'bar')


@mock.patch.object(Metadata, 'prop')
def test_metadata_ogprop(prop):
    m = Metadata()
    ret = m.ogprop('foo', 'bar')
    assert ret == prop.return_value
    prop.assert_called_once_with('og', 'foo', 'bar')


@mock.patch.object(Metadata, 'ogprop')
@mock.patch.object(Metadata, 'twitterprop')
@mock.patch.object(Metadata, 'itemprop')
def test_metadata_title(itemprop, ogprop, twitterprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    m = Metadata(title='foo')
    m.render()
    ogprop.assert_called_once_with('title', 'foo')
    twitterprop.assert_called_once_with('title', 'foo')
    itemprop.assert_called_once_with('name', 'foo')


@mock.patch.object(Metadata, 'simple')
@mock.patch.object(Metadata, 'ogprop')
@mock.patch.object(Metadata, 'twitterprop')
@mock.patch.object(Metadata, 'itemprop')
def test_metadata_description(itemprop, ogprop, twitterprop, simple):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    simple.return_value = ''
    m = Metadata(description='foo')
    m.render()
    ogprop.assert_called_once_with('description', 'foo')
    twitterprop.assert_called_once_with('description', 'foo')
    itemprop.assert_called_once_with('description', 'foo')


@mock.patch(MOD + 'full_url')
def test_metadata_make_full(full_url):
    ret = Metadata.make_full('foo')
    full_url.assert_called_once_with('foo')
    assert ret == full_url.return_value


@mock.patch(MOD + 'full_url')
def test_metadata_make_full_with_full_url(full_url):
    ret = Metadata.make_full('http://foo/')
    assert not full_url.called


@mock.patch(MOD + 'full_url')
def test_metadata_make_full_special_case(full_url):
    # This is expected, and it's OK. We hope developers aren't that dumb.
    Metadata.make_full('httpfoo')
    assert not full_url.called


@mock.patch(MOD + 'Metadata.make_full')
def test_metadata_assign_image(make_full):
    m = Metadata(thumbnail='foo.png')
    make_full.assert_called_once_with('foo.png')
    assert m.thumbnail == make_full.return_value


@mock.patch.object(Metadata, 'ogprop')
@mock.patch.object(Metadata, 'twitterprop')
@mock.patch.object(Metadata, 'itemprop')
@mock.patch(MOD + 'Metadata.make_full')
def test_metadata_image(make_full, ogprop, twitterprop, itemprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    make_full.return_value = 'foobar'
    m = Metadata(thumbnail='foo')
    m.render()
    ogprop.assert_called_once_with('image', 'foobar')
    twitterprop.assert_called_once_with('image', 'foobar')
    itemprop.assert_called_once_with('image', 'foobar')


@mock.patch(MOD + 'Metadata.make_full')
def test_metadata_assign_url(make_full):
    m = Metadata(url='/foo')
    make_full.assert_called_once_with('/foo')
    assert m.url == make_full.return_value


@mock.patch.object(Metadata, 'ogprop')
@mock.patch.object(Metadata, 'twitterprop')
@mock.patch.object(Metadata, 'itemprop')
@mock.patch(MOD + 'Metadata.make_full')
def test_metadata_url(make_full, ogprop, twitterprop, itemprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    make_full.return_value = 'foobar'
    m = Metadata(url='foo')
    m.render()
    ogprop.assert_called_once_with('url', 'foobar')
    twitterprop.assert_called_once_with('url', 'foobar')
    itemprop.assert_called_once_with('url', 'foobar')


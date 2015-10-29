"""
test_meta.py: Unit tests for ``bottle_utils.meta`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

import sys

import mock

import bottle_utils.meta as mod

PY2 = sys.version_info.major == 2
MOD = 'bottle_utils.meta.'


@mock.patch.object(mod.MetaBase, 'render')
def test_meta_base_str_calls_render(render):
    m = mod.MetaBase()
    render.return_value = 'foo'
    assert str(m) == 'foo'
    assert render.called


def test_simple_meta():
    expected = '<meta foo="bar" content="baz">'
    assert mod.SimpleMetadata.meta('foo', 'bar', 'baz') == expected


def test_simple():
    m = mod.SimpleMetadata()
    assert str(m) == ''


def test_simple_title():
    m = mod.SimpleMetadata(title='foo')
    s = m.render()
    assert '<title>foo</title>' in s


@mock.patch.object(mod.SimpleMetadata, 'simple')
def test_simple_description(simple):
    m = mod.SimpleMetadata(description='foo')
    m.render()
    simple.assert_called_once_with('description', 'foo')


@mock.patch.object(mod.Metadata, 'meta')
def test_metadata_prop(meta):
    m = mod.Metadata()
    ret = m.prop('foo', 'bar', 'baz')
    assert ret == meta.return_value
    meta.assert_called_once_with('property', 'foo:bar', 'baz')


@mock.patch.object(mod.Metadata, 'meta')
def test_metadata_simple(meta):
    m = mod.Metadata()
    ret = m.simple('foo', 'bar')
    assert ret == meta.return_value
    meta.assert_called_once_with('name', 'foo', 'bar')


@mock.patch.object(mod.Metadata, 'meta')
def test_metadata_nameprop(meta):
    m = mod.Metadata()
    ret = m.nameprop('foo', 'bar', 'baz')
    assert ret == meta.return_value
    meta.assert_called_once_with('name', 'foo:bar', 'baz')


@mock.patch.object(mod.Metadata, 'meta')
def test_metadata_itemprop(meta):
    m = mod.Metadata()
    ret = m.itemprop('foo', 'bar')
    assert ret == meta.return_value
    meta.assert_called_once_with('itemprop', 'foo', 'bar')


@mock.patch.object(mod.Metadata, 'nameprop')
def test_metadata_twitterprop(nameprop):
    m = mod.Metadata()
    ret = m.twitterprop('foo', 'bar')
    assert ret == nameprop.return_value
    nameprop.assert_called_once_with('twitter', 'foo', 'bar')


@mock.patch.object(mod.Metadata, 'prop')
def test_metadata_ogprop(prop):
    m = mod.Metadata()
    ret = m.ogprop('foo', 'bar')
    assert ret == prop.return_value
    prop.assert_called_once_with('og', 'foo', 'bar')


@mock.patch.object(mod.Metadata, 'ogprop')
@mock.patch.object(mod.Metadata, 'twitterprop')
@mock.patch.object(mod.Metadata, 'itemprop')
def test_metadata_title(itemprop, twitterprop, ogprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    m = mod.Metadata(title='foo')
    m.render()
    ogprop.assert_called_once_with('title', 'foo')
    twitterprop.assert_called_once_with('title', 'foo')
    itemprop.assert_called_once_with('name', 'foo')


@mock.patch.object(mod.Metadata, 'simple')
@mock.patch.object(mod.Metadata, 'ogprop')
@mock.patch.object(mod.Metadata, 'twitterprop')
@mock.patch.object(mod.Metadata, 'itemprop')
def test_metadata_description(itemprop, twitterprop, ogprop, simple):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    simple.return_value = ''
    m = mod.Metadata(description='foo')
    m.render()
    ogprop.assert_called_once_with('description', 'foo')
    twitterprop.assert_called_once_with('description', 'foo')
    itemprop.assert_called_once_with('description', 'foo')


@mock.patch.object(mod, 'full_url')
def test_metadata_make_full(full_url):
    ret = mod.Metadata.make_full('foo')
    full_url.assert_called_once_with('foo')
    assert ret == full_url.return_value


@mock.patch.object(mod, 'full_url')
def test_metadata_make_full_with_full_url(full_url):
    mod.Metadata.make_full('http://foo/')
    assert not full_url.called


@mock.patch.object(mod, 'full_url')
def test_metadata_make_full_special_case(full_url):
    # This is expected, and it's OK. We hope developers aren't that dumb.
    mod.Metadata.make_full('httpfoo')
    assert not full_url.called


@mock.patch.object(mod.Metadata, 'make_full')
def test_metadata_assign_image(make_full):
    m = mod.Metadata(thumbnail='foo.png')
    make_full.assert_called_once_with('foo.png')
    assert m.thumbnail == make_full.return_value


@mock.patch.object(mod.Metadata, 'ogprop')
@mock.patch.object(mod.Metadata, 'twitterprop')
@mock.patch.object(mod.Metadata, 'itemprop')
@mock.patch.object(mod.Metadata, 'make_full')
def test_metadata_image(make_full, itemprop, twitterprop, ogprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    make_full.return_value = 'foobar'
    m = mod.Metadata(thumbnail='foo')
    m.render()
    ogprop.assert_called_once_with('image', 'foobar')
    twitterprop.assert_called_once_with('image', 'foobar')
    itemprop.assert_called_once_with('image', 'foobar')


@mock.patch.object(mod.Metadata, 'make_full')
def test_metadata_assign_url(make_full):
    m = mod.Metadata(url='/foo')
    make_full.assert_called_once_with('/foo')
    assert m.url == make_full.return_value


@mock.patch.object(mod.Metadata, 'ogprop')
@mock.patch.object(mod.Metadata, 'twitterprop')
@mock.patch.object(mod.Metadata, 'itemprop')
@mock.patch.object(mod.Metadata, 'make_full')
def test_metadata_url(make_full, itemprop, twitterprop, ogprop):
    itemprop.return_value = ogprop.return_value = twitterprop.return_value = ''
    make_full.return_value = 'foobar'
    m = mod.Metadata(url='foo')
    m.render()
    ogprop.assert_called_once_with('url', 'foobar')
    twitterprop.assert_called_once_with('url', 'foobar')
    itemprop.assert_called_once_with('url', 'foobar')

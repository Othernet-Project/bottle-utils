"""
meta.py: Helpers for generating meta tags

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

from bottle import request

from .common import *


class MetaBase(object):
    def render(self):
        return ''

    def __str__(self):
        return self.render()


class SimpleMetadata(MetaBase):
    def __init__(self, title='', description=''):
        self.title = title
        self.description = description

    @staticmethod
    def meta(attr, name, value):
        """ <meta $attr=$name content=$value> """
        return '<meta %s="%s" content="%s">' % (attr, attr_escape(name),
                                                attr_escape(value))

    def simple(self, name, value):
        """ <meta name=$name content=$value> """
        return self.meta('name', name, value)

    def render(self):
        s = ''
        if self.title:
            s += '<title>%s</title>' % html_escape(self.title)
        if self.description:
            s += self.simple('description', self.description)
        return super(SimpleMetadata, self).render() + s


class Metadata(SimpleMetadata):
    def __init__(self, title='', description='', thumbnail='', url=''):
        super(Metadata, self).__init__(title, description)
        if (not thumbnail) or thumbnail.startswith('http'):
            self.thumbnail = thumbnail
        self.thumbnail = thumbnail and self.make_full(thumbnail) or ''
        self.url = url and self.make_full(url) or ''

    @staticmethod
    def make_full(url):
        if (not url) or url.startswith('http'):
            return url
        return full_url(url)

    def prop(self, namespace, name, value):
        """ <meta property=$namespace:$name content=$value> """
        prop_name = '%s:%s' % (attr_escape(namespace), attr_escape(name))
        return self.meta('property', prop_name, value)

    def nameprop(self, namespace, name, value):
        """ <meta name=$namespace:$name content=$value> """
        prop_name = '%s:%s' % (attr_escape(namespace), attr_escape(name))
        return self.meta('name', prop_name, value)

    def itemprop(self, name, value):
        """ <meta itemprop=$name content=$value> """
        return self.meta('itemprop', name, value)

    def twitterprop(self, name, value):
        """ <meta name=twitter:$name content=$value> """
        return self.nameprop('twitter', name, value)

    def ogprop(self, name, value):
        """ <meta property=og:$name content=$value> """
        return self.prop('og', name, value)

    def render(self):
        s = ''
        if self.title:
            s += self.ogprop('title', self.title)
            s += self.twitterprop('title', self.title)
            s += self.itemprop('name', self.title)
        if self.description:
            s += self.ogprop('description', self.description)
            s += self.twitterprop('description', self.description)
            s += self.itemprop('description', self.description)
        if self.thumbnail:
            s += self.ogprop('image', self.thumbnail)
            s += self.twitterprop('image', self.thumbnail)
            s += self.itemprop('image', self.thumbnail)
        if self.url:
            s += self.ogprop('url', self.url)
            s += self.twitterprop('url', self.url)
            s += self.itemprop('url', self.url)
        return super(Metadata, self).render() + s


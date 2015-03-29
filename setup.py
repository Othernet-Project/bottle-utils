import os
from setuptools import setup, find_packages

def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = '0.3'
RELEASE = '0.3.1'

setup(
    name='bottle-utils',
    version=RELEASE,
    author='Outernet Inc',
    author_email='branko@outernet.is',
    description=('Assortment of frequently used utilities for Bottle '
                   'framework'),
    license='BSD',
    keywords='bottle utils i18n http lazy csrf ajax',
    url='http://outernet-project.github.io/bottle-utils/',
    packages=find_packages(),
    long_description=read('README.rst'),
    install_requires=[
        'bottle-utils-common~=%s' % VERSION,
        'bottle-utils-ajax~=%s' % VERSION,
        'bottle-utils-csrf~=%s' % VERSION,
        'bottle-utils-flash~=%s' % VERSION,
        'bottle-utils-html~=%s' % VERSION,
        'bottle-utils-http~=%s' % VERSION,
        'bottle-utils-i18n~=%s' % VERSION,
        'bottle-utils-lazy~=%s' % VERSION,
        'bottle-utils-meta~=%s' % VERSION,
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

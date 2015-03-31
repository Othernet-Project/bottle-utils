import os
from setuptools import setup, find_packages


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


MAJOR = '0.3'
NEXT = '0.4'

setup(
    name='bottle-utils',
    version='0.3.2',
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
        'bottle-utils-common >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-ajax >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-csrf >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-flash >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-html >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-http >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-i18n >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-lazy >=%s, <%s' % (MAJOR, NEXT),
        'bottle-utils-meta >=%s, <%s' % (MAJOR, NEXT),
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

import os
from setuptools import setup, find_packages


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

import bottle_utils


setup(
    name='bottle-utils',
    version=bottle_utils.__version__,
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
        'bottle>=0.12.7',
        'python-dateutil>=2.2',
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

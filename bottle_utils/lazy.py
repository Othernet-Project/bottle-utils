"""
.. module:: bottle_utils.lazy
   :synopsis: Lazy evaluation

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from functools import wraps

from .common import to_unicode, to_bytes

__all__ = ('Lazy', 'CachingLazy', 'lazy', 'caching_lazy')


class Lazy(object):
    """
    Lazy proxy object. This proxy always evaluates the function when it is
    used.

    Any positional and keyword arguments that are passed to the constructor are
    stored and passed to the function except the ``_func`` argument which is
    the function itself. Because of this, the wrapped callable cannot use an
    argument named ``_func`` itself.
    """

    def __init__(self, _func, *args, **kwargs):
        self._func = _func
        self._args = args
        self._kwargs = kwargs

    def _eval(self):
        return self._func(*self._args, **self._kwargs)

    @staticmethod
    def _eval_other(other):
        try:
            return other._eval()
        except AttributeError:
            return other

    def __getattr__(self, attr):
        obj = self._eval()
        return getattr(obj, attr)

    # We don't need __setattr__ and __delattr__ because the proxy object is not
    # really an object.

    def __getitem__(self, key):
        obj = self._eval()
        return obj.__getitem__(key)

    @property
    def __class__(self):
        return self._eval().__class__

    def __repr__(self):
        return repr(self._eval())

    def __str__(self):
        return to_unicode(self._eval())

    def __bytes__(self):
        return to_bytes(self._eval())

    def __call__(self):
        return self._eval()()

    def __format__(self, format_spec):
        return self._eval().__format__(format_spec)

    def __mod__(self, other):
        return self._eval().__mod__(other)

    # Being explicit about all comparison methods to avoid double-calls

    def __lt__(self, other):
        other = self._eval_other(other)
        return self._eval() < other

    def __le__(self, other):
        other = self._eval_other(other)
        return self._eval() <= other

    def __gt__(self, other):
        other = self._eval_other(other)
        return self._eval() > other

    def __ge__(self, other):
        other = self._eval_other(other)
        return self._eval() >= other

    def __eq__(self, other):
        other = self._eval_other(other)
        return self._eval() == other

    def __ne__(self, other):
        other = self._eval_other(other)
        return self._eval() != other

    # We mostly use this for strings, so having just __add__ is fine

    def __add__(self, other):
        other = self._eval_other(other)
        return self._eval() + other

    def __radd__(self, other):
        return self._eval_other(other) + self._eval()

    def __bool__(self):
        return bool(self._eval())

    __nonzero__ = __bool__

    def __hash__(self):
        return hash(self._eval())


class CachingLazy(Lazy):
    """
    Caching version of the :py:class:`~Lazy` class. Unlike the parent class,
    this class only evaluates the callable once, and remembers the resutls. On
    subsequent use, it returns the original result. This is probably closer to
    the behavior of a normal return value.
    """

    def __init__(self, _func, *args, **kwargs):
        self._called = False
        self._cached = None
        super(CachingLazy, self).__init__(_func, *args, **kwargs)

    def _eval(self):
        if self._called:
            return self._cached
        self._called = True
        self._cached = self._func(*self._args, **self._kwargs)
        return self._cached


def lazy(fn):
    """
    Convert a function into lazily evaluated version. This decorator causes the
    function to return a :py:class:`~Lazy` proxy instead of the actual results.

    Usage is simple::

        @lazy
        def my_lazy_func():
            return 'foo'

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return Lazy(fn, *args, **kwargs)
    return wrapper


def caching_lazy(fn):
    """
    Convert a function into cached lazily evaluated version. This decorator
    modifies the function to return a :py:class:`~CachingLazy` proxy instead of
    the actual result.

    This decorator has no arguments::

        @caching_lazy
        def my_lazy_func():
            return 'foo'

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return CachingLazy(fn, *args, **kwargs)
    return wrapper

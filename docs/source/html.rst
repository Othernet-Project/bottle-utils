Template helpers (``bottle_utils.html``)
========================================

Contents of this module are mostly meant to be used inside the view templates,
but their usage is not limited to templates by any means. ``bottle_utils.html``
contains a few data-formatting functions as well as shortcuts for generating
HTML snippets and binding data to form fields.

Basic usage
-----------

One way to make the module contents available to templates is to add the module
itself as a default template variable.::

    import bottle
    from bottle_utils import html
    bottle.BaseTemplate.defaults['h'] = html

This allows you to use the module members by access the ``h`` variable in
templates::

    <html {{! h.attr('lang', request.locale }}>

.. note::
    If your tempate engine auto-escapes HTML, you need to instruct it to
    unescape strings gneerated by some of the helper functions. For instance,
    in Bottle's SimpleTemplate engine, you need to enclose the strings in ``{{!
    }}``.

Data formatting
---------------

.. automodule:: bottle_utils.html

.. autofunction:: hsize
.. autofunction:: plur
.. autofunction:: strft
.. autofunction:: trunc
.. autofunction:: yesno

HTML rendering
--------------

.. autofunction:: tag
.. autofunction:: link_other(label, url, path, wrapper=lambda l, *kw: l, **kwargs)
.. autofunction:: vinput
.. autofunction:: varea
.. autofunction:: vcheckbox
.. autofunction:: vselect
.. autofunction:: form

URL handling
------------

.. autoclass:: QueryDict
   :members: __init__, add_qparam, set_qparam, del_qparam, to_qs
.. autofunction:: add_qparam
.. autofunction:: set_qparam
.. autofunction:: del_qparam
.. autofunction:: urlquote
.. autofunction:: urlunquote
.. autofunction:: quote_dict
.. autofunction:: quoted_url
.. autofunction:: full_quoted_url

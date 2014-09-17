Template helpers (``bottle_utils.html``)
========================================

Contents of this module are mostly meant to be used inside the Bottle's
SimpleTemplate templates. It contains a few data-formatting functions as well
as shortcuts for generating HTML snippets and binding data to form fields.

One way to make the module contents available to templates is to add the module 
itself as a default template variable.::

    import bottle
    from bottle_utils import html
    bottle.BaseTemplate.defaults['h'] = html

This allows you to use the module members by access the ``h`` variable in
templates::

    <html {{! h.attr('lang', request.locale }}>

Note that, since some of these function generate HTML markup, you need to make
sure they are not escaped by Bottle. Use the ``{{! }}`` syntax (with bang, !) 
to allow unescaped HTML markup.

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
.. autofunction:: field_error
.. autofunction:: form_errors

URL handling
------------

.. autofunction:: add_qparam

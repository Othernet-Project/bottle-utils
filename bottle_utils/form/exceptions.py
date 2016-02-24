class ValidationError(Exception):
    """
    Error raised during field and form validation. The erorr object can be
    initialized using a message string, and two optional parameters, ``params``
    and ``is_form``.

    The ``params`` is a dictionary of key-value pairs that are used to fill the
    message in with values that are only known at runtime. For example, if the
    message is ``'{value} is invalid for this field'``, we can pass a
    ``params`` argument that looks like ``{'value': foo}``. The ``format()``
    method is called on the message.

    Note that ``message`` is a key pointing to a value in the ``messages``
    dictionary on the form and field objects, not the actual message.
    """

    def __init__(self, message, params=None, is_form=False):
        self.message = message
        self.params = params
        self.is_form = is_form
        super(ValidationError, self).__init__(message)

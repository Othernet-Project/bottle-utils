import dateutil.parser

from bottle_utils.common import basestring

try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x

from .exceptions import ValidationError


class Validator(object):
    """
    Base validator class. This calss does not do much on its own. It is used
    primarily to build other validators.

    The :py:meth:`~validate` method in the subclass performs the validation and
    raises a :py:class:`~bottle_utils.form.exceptions.ValidationError`
    exception when the data is invalid.

    The ``messages`` argument is used to override the error messages for the
    validators. This argument should be a dictionary that maps the error names
    used by individual validators to the new messages. The error names used by
    validators is documented for each class. You can also dynamically obtain
    the names by inspecting the ``messages`` property on each of the validator
    classes.

    """

    #: Mapping between errors and their human-readabile messages
    messages = {}

    def __init__(self, messages={}):
        # Make sure the defaults are copied so updating the messages attribute
        # doesn't affect the class' version or any other instances.
        self.messages = self.messages.copy()
        self.messages.update(messages)

    def __call__(self, data):
        self.validate(data)

    def validate(self, data):
        """
        Perform actual validation over data. Should raise
        :py:class:`~bottle_utils.form.exceptions.ValidationError`
        if data does not pass the validation.

        Two arguments are passed to the validation error, the error name and a
        dictionary with extra parameters (usually with ``value`` key that
        points to the value).

        Error message is constructed based on the arguments, passed to the
        exception by looking up the key in the :py:attr:`~messages` property to
        obtain the message, and then interpolating any extra parameters into
        the message.

        This method does not need to return anything.
        """
        raise NotImplementedError()


class Required(Validator):
    """
    Validates the presence of data. Technically, this validator fails for any
    data that is an empty string, a string that only contains whitespace, or
    data that is not a string and evaluates to ``False`` when coerced into
    boolean (e.g., 0, empty arrays and dicts, etc).

    :error name(s): required
    """

    messages = {
        'required': _('This field is required'),
    }

    def validate(self, data):
        if not data or isinstance(data, basestring) and not data.strip():
            # Translator, represents empty field's value
            raise ValidationError('required', {'value': _('(empty)')})


class DateValidator(Validator):
    """
    Validates date fields. This validator attempts to parse the data as date (or
    date/time) data. When the data cannot be parsed, it fails.

    :error name(s): date
    """
    messages = {
        'date': _('{value} does not look like a valid date'),
    }

    def validate(self, value):
        try:
            dateutil.parser.parse(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError('date', {'value': value, 'exc': str(exc)})


class InRangeValidator(Validator):
    """
    Validates that value is within a range between two values. This validator
    works with any objects that support ``>`` and ``<`` operators.

    The ``min_value`` and ``max_value`` arguments are used to set the lower and
    upper bounds respectively. The check for those bounds are only done when
    the arguments are supplied so, when both arguments are omitted, this
    validator is effectively pass-through.

    :error name(s): min_val, max_val
    """

    messages = {
        'min_val': _('{value} is too small'),
        'max_val': _('{value} is too large'),
    }

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super(InRangeValidator, self).__init__(**kwargs)

    def validate(self, value):
        try:
            if self.min_value is not None and self.min_value > value:
                raise ValidationError(
                    'min_val', {'value': value, 'min': self.min_value})
            if self.max_value is not None and self.max_value < value:
                raise ValidationError(
                    'max_val', {'value': value, 'max': self.max_value})
        except Exception:
            raise ValidationError('generic', {'value': value})

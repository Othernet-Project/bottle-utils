import dateutil.parser

from bottle_utils.common import basestring

try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x

from .exceptions import ValidationError


class Validator(object):
    messages = {}

    def __init__(self, messages={}):
        # Make sure the defaults are copied so updating the messages attribute
        # doesn't affect the class' version or any other instances.
        self.messages = self.messages.copy()
        self.messages.update(messages)

    def __call__(self, data):
        self.validate(data)

    def validate(self, data):
        """Perform actual validation over data. Should raise `ValidationError`
        if data does not pass the validation."""
        raise NotImplementedError()


class Required(Validator):
    messages = {
        'required': _('This field is required'),
    }

    def validate(self, data):
        if not data or isinstance(data, basestring) and not data.strip():
            # Translator, represents empty field's value
            raise ValidationError('required', {'value': _('(empty)')})


class DateValidator(Validator):
    messages = {
        'date': _('{value} does not look like a valid date'),
    }

    def validate(self, value):
        try:
            return dateutil.parser.parse(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError('date', {'value': value, 'exc': str(exc)})


class InRangeValidator(Validator):
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

from bottle_utils import html
from bottle_utils.common import basestring, unicode

try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x

from .exceptions import ValidationError
from .labels import Label
from .validators import DateValidator


class DormantField(object):

    def __init__(self, field_cls, args, kwargs):
        self.field_cls = field_cls
        self.args = args
        self.kwargs = kwargs

    def bind(self, name):
        return self.field_cls(name=name, *self.args, **self.kwargs)


class Field(object):
    _id_prefix = 'id_'
    _label_cls = Label

    # Translators, used as generic error message in form fields, 'value' should
    # not be translated.
    generic_error = _('Invalid value for this field')
    messages = {}
    type = 'text'

    def __new__(cls, *args, **kwargs):
        if 'name' in kwargs:
            return super(Field, cls).__new__(cls)
        return DormantField(cls, args, kwargs)

    def __init__(self, label=None, validators=None, value=None, name=None,
                 messages={}, **options):
        self.name = name
        self.label = self._label_cls(label, self._id_prefix + name)
        self.validators = validators or []
        self.value = value() if callable(value) else value
        self.processed_value = None
        self.is_value_bound = False
        self._error = None
        self.options = options

        self.messages = self.messages.copy()

        # Collect default messages from all validators into the messages dict
        for validator in self.validators:
            self.messages.update(validator.messages)

        # Update the messages dict with any user-supplied messages
        self.messages.update(messages)

    def bind_value(self, value):
        self.value = value
        self.is_value_bound = True

    def is_valid(self):
        try:
            self.processed_value = self.parse(self.value)
        except ValueError as exc:
            self._error = ValidationError('generic', {'value': self.value})
            return False

        for validate in self.validators:
            try:
                validate(self.processed_value)
            except ValidationError as exc:
                self._error = exc
                return False

        return True

    @property
    def error(self):
        if not self._error:
            return ''
        return self.messages.get(self._error.message, self.generic_error)

    def parse(self, value):
        """Subclasses should return the value in it's correct type. In case the
        passed in value cannot be cast into it's correct type, the method
        should raise a `ValueError` exception with an appropriate error
        message."""
        raise NotImplementedError()


class StringField(Field):

    def parse(self, value):
        if value is None:
            return ''
        return unicode(value)


class PasswordField(StringField):

    type = 'password'

    def render(self):
        return html.vinput(self.name,
                           {},
                           _type='password',
                           _id=self._id_prefix + self.name,
                           **self.options)


class HiddenField(StringField):

    type = 'hidden'


class EmailField(StringField):
    pass


class TextAreaField(StringField):

    type = 'textarea'


class DateField(StringField):

    def __init__(self, label, validators=None, value=None, **options):
        validators = [DateValidator()] + list(validators or [])
        super(DateField, self).__init__(label,
                                        validators=validators,
                                        value=value,
                                        **options)


class FileField(Field):

    type = 'file'

    def parse(self, value):
        return value


class IntegerField(Field):

    def parse(self, value):
        if value is None:
            return value

        try:
            return int(value)
        except Exception:
            raise ValueError(_("Invalid value for an integer."))


class FloatField(Field):

    def parse(self, value):
        if value is None:
            return value

        try:
            return float(value)
        except Exception:
            raise ValueError(_("Invalid value for a float."))


class BooleanField(Field):

    type = 'checkbox'

    def __init__(self, label, validators=None, value=None, default=False,
                 **options):
        self.default = default
        self.expected_value = value
        super(BooleanField, self).__init__(label,
                                           validators=validators,
                                           value=value,
                                           **options)

    def parse(self, value):
        if not value or isinstance(value, basestring):
            return self.expected_value == value
        return self.expected_value in value


class SelectField(Field):

    type = 'select'

    def __init__(self, label, validators=None, value=None, choices=None,
                 **options):
        self.choices = choices or tuple()
        super(SelectField, self).__init__(label,
                                          validators=validators,
                                          value=value,
                                          **options)

    def parse(self, value):
        chosen = unicode(value)
        for (candidate, label) in self.choices:
            if unicode(candidate) == chosen:
                return chosen if value is not None else value

        raise ValueError(_("This is not a valid choice."))

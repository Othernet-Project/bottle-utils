from bottle_utils import html
from bottle_utils.common import basestring, unicode

try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x

from .exceptions import ValidationError
from .validators import DateValidator


class DormantField(object):
    """
    Proxy for unbound fields. This class holds the the field constructor
    arguments until the data can be bound to it.

    You never need to use this class directly.
    """

    def __init__(self, field_cls, args, kwargs):
        self.field_cls = field_cls
        self.args = args
        self.kwargs = kwargs

    def bind(self, name):
        return self.field_cls(name=name, *self.args, **self.kwargs)


class Field(object):
    """
    Form field base class. This class provides the base functionality for all
    form fields.

    The ``label`` argument is used to specify the field's label.

    The ``validators`` argument is used to specify the validators that will be
    used on the field data.

    If any data should be bound to a field, the ``value`` argument can be used to
    specify it. Value can be a callable, in which case it is called and its
    return value used as ``value``.

    The ``name`` argument is used to specify the field name.

    The ``messages`` argument is used to customize the validation error
    messages. These override any messages found in the :py:attr:`~messages`
    attribute.

    Any extra keyword attributes passed to the constructor are stored as
    :py:attr:`~options` property on the instance.
    """

    #: Field ID attribute prefix (this is prepended to the field name)
    _id_prefix = ''

    #: Generic error message to be used when no messages match the validation
    #: error.
    # Translators, used as generic error message in form fields, 'value' should
    # not be translated.
    generic_error = _('Invalid value for this field')
    #: Validation error messages.
    messages = {}
    #: Field markup type. This is arbitrary and normally used in the templates
    #: to differentiate between field types. It is up to the template author to
    #: decide how this should be treated.
    type = 'text'

    def __new__(cls, *args, **kwargs):
        if 'name' in kwargs:
            return super(Field, cls).__new__(cls)
        return DormantField(cls, args, kwargs)

    def __init__(self, label=None, validators=None, value=None, name=None,
                 messages={}, **options):
        #: Field name
        self.name = name

        #: Field label
        self.label = label

        #: Field validators
        self.validators = validators or []

        #: Raw value of the field
        self.value = value() if callable(value) else value

        #: Processed value of the field
        self.processed_value = None

        #: Whether value is bound to this field
        self.is_value_bound = False

        self._error = None

        #: Extra keyword argument passed to the constructor
        self.options = options

        # Copy the messages so that modifying them does not result in class'
        # ``messages`` attribute to be altered.
        self.messages = self.messages.copy()

        # Collect default messages from all validators into the messages dict
        for validator in self.validators:
            self.messages.update(validator.messages)

        # Update the messages dict with any user-supplied messages
        self.messages.update(messages)

    def bind_value(self, value):
        """
        Binds a value. This method also sets the :py:attr:`~is_value_bound`
        property to ``True``.
        """
        self.value = value
        self.is_value_bound = True

    def is_valid(self):
        """
        Validate form field and return ``True`` is data is valid. If there is
        an error during Validation, the error object is stored in the
        :py:attr:`~_error` property. Before validation, the raw value is
        processed using the :py:meth:`~parse` method, and stored in
        :py:attr:`~processed_value` attribute.

        When parsing fails with ``ValueError`` exception, a 'generic' error is
        stored. The default message for this error is stored in the
        :py:attr:`~generic_error` property, and can be customized by passing
        a ``'generic'`` message as part of the ``messages`` constructor
        argument.
        """
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
        """
        Human readable error message. This property evaluates to empty string
        if there are no errors.
        """
        if not self._error:
            return ''
        return self.messages.get(self._error.message, self.generic_error)

    def parse(self, value):
        """
        Parse the raw value and convert to Python object. Subclasses should
        return the value in it's correct type. In case the passed in value
        cannot be cast into it's correct type, the method should raise a
        ``ValueError`` exception with an appropriate error message.
        """
        raise NotImplementedError()


class StringField(Field):
    """
    Field for working with string values.

    :Python type: str (unicode in Python 2.x)
    :type: text
    """

    def parse(self, value):
        if value is None:
            return ''
        return unicode(value)


class PasswordField(StringField):
    """
    Field for working with passwords.

    :Python type: str (unicode in Python 2.x)
    :type: password
    """

    type = 'password'


class HiddenField(StringField):
    """
    Field for working with hidden inputs.

    :Python type: str (unicode in Python 2.x)
    :type: hidden
    """

    type = 'hidden'


class EmailField(StringField):
    """
    Field for working with emails.

    :Python type: str (unicode in Python 2.x)
    :type: text
    """
    pass


class TextAreaField(StringField):
    """
    Field for working with textareas.

    :Python type: str (unicode in Python 2.x)
    :type: textarea
    """

    type = 'textarea'


class DateField(StringField):
    """
    Field for working with dates. This field overloads the base class'
    constructor to add a :py:class:`~bottle_utils.validators.DateValidator`.

    :Python type: str (unicode in Python 2.x)
    :type: text
    """

    def __init__(self, label, validators=None, value=None, **options):
        validators = [DateValidator()] + list(validators or [])
        super(DateField, self).__init__(label,
                                        validators=validators,
                                        value=value,
                                        **options)


class FileField(Field):
    """
    Field for working with file uploads.

    :Python type: raw value
    :type: file
    """

    type = 'file'

    def parse(self, value):
        return value


class IntegerField(Field):
    """
    Field for working with integers.

    :Python type: int
    :type: text
    """

    def parse(self, value):
        if value is None:
            return value

        try:
            return int(value)
        except Exception:
            raise ValueError(_("Invalid value for an integer."))


class FloatField(Field):
    """
    Field for working with floating-point numbers.

    :Python type: float
    :type: text
    """

    def parse(self, value):
        if value is None:
            return value

        try:
            return float(value)
        except Exception:
            raise ValueError(_("Invalid value for a float."))


class BooleanField(Field):
    """
    Field for working with boolean values.

    Two additional constructor arguments are added. The ``default`` argument is
    used to specify the default state of the field, which can be used in the
    template to, for instance, check or uncheck a checkbox or radio button. The
    ``expected_value`` is the base value of the field against which the bound
    value is checked: if they match, the Python value of the field is ``True``.

    :Python type: bool
    :type: checkbox
    """

    type = 'checkbox'

    def __init__(self, label, validators=None, value=None, default=False,
                 **options):
        #: Default state of the field
        self.default = default
        #: Base value of the field against which bound value is checked
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
    """
    Field for dealing with select lists.

    The ``choices`` argument is used to specify the list of value-label pairs
    that are used to present the valid choices in the interface. The field
    value is then checked against the list of value and the parser validates
    whether the supplied value is among the valid ones.

    :Python type: str (unicode in Python 2.x)
    :type: select
    """

    type = 'select'

    def __init__(self, label, validators=None, value=None, choices=None,
                 **options):
        #: Iterable of value-label pairs of valid choices
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

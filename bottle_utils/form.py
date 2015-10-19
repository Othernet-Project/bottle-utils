"""
.. module:: bottle_utils.form
   :synopsis: Form processing and validation library
.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""


import dateutil.parser

from bottle_utils import html
from bottle_utils.common import basestring, unicode

try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x


class ValidationError(Exception):

    def __init__(self, message, params, is_form=False):
        self.message = message
        self.params = params
        self.is_form = is_form
        super(ValidationError, self).__init__(message)

    def __str__(self):
        """Calls renderer function"""
        return self.render()

    def __unicode__(self):
        """Calls renderer function"""
        return self.render()


class Label(object):

    def __init__(self, text, for_element):
        self.text = text
        self.for_element = for_element

    def __str__(self):
        """Calls renderer function"""
        return self.text

    def __unicode__(self):
        """Calls renderer function"""
        return self.text

    def __mod__(self, other):
        return self.text % other


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

    def render(self):
        return html.vinput(self.name,
                           {},
                           _type='password',
                           _id=self._id_prefix + self.name,
                           **self.options)


class HiddenField(StringField):
    pass


class EmailField(StringField):
    pass


class TextAreaField(StringField):
    pass


class DateField(StringField):

    def __init__(self, label, validators=None, value=None, **options):
        validators = [DateValidator()] + list(validators or [])
        super(DateField, self).__init__(label,
                                        validators=validators,
                                        value=value,
                                        **options)


class FileField(Field):

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


class Form(object):
    """Base form class to be subclassed. Definition of new forms:

    class NewForm(Form):
        field1 = Field('Field 1')
        field2 = Field('Field 2', [Required])

        def preprocess_field1(self, value):
            return value.replace('this', 'that')

        def postprocess_field1(self, value):
            return value + 'done'

    Preprocessors can be defined for individual fields, and are ran before any
    validation happens over the field's data. Preprocessors are also allowed
    to raise `ValidationError`, though their actual purpose is to perform some
    manipulation over the incoming data, before it is passed over to the
    validators. The return value of the preprocessor is the value that is going
    to be validated further.

    Postprocessors perform a similar purpose as preprocessors, only they are
    invoked after and if the field-level validation passed. Their return value
    is the value that is going to be the stored as cleaned / validated data.
    """
    _pre_processor_prefix = 'preprocess_'
    _post_processor_prefix = 'postprocess_'

    # Translators, used as generic error message in forms, 'value' should not
    # be translated.
    generic_error = _('Form contains invalid data.')
    messages = {}

    def __init__(self, data=None, messages={}):
        """Initialize forms.

        :param data:     Dict-like object containing the form data to be
                         validated, or the initial values of a new form
        """
        self._has_error = False
        self._error = None
        self.processed_data = {}
        self.messages = self.messages.copy()
        self.messages.update(messages)
        self._bind(data)

    def _bind(self, data):
        """Binds field names and values to the field instances."""
        for field_name, dormant_field in self.fields.items():
            field_instance = dormant_field.bind(field_name)
            setattr(self, field_name, field_instance)
            if data is not None:
                field_instance.bind_value(data.get(field_name))

    @property
    def field_messages(self):
        """ Dictionary of all field error messages

        This value maps the field names to error message maps. Field names are
        mapped to fields' messages property, which maps error type to actual
        message. This dictionary can also be used to modify the messages
        because message mappings are not copied.
        """
        messages = {}
        for field_name, field in self.fields.items():
            messages[field_name] = field.messages
        return messages

    @property
    def fields(self):
        """Returns a dictionary of all the fields found on the form instance.
        The return value is never cached so dynamically adding new fields to
        the form is allowed."""
        types = (Field, DormantField)
        is_form_field = lambda name: isinstance(getattr(self, name), types)
        ignored_attrs = ['fields', 'field_messages']
        return dict((name, getattr(self, name)) for name in dir(self)
                    if name not in ignored_attrs and is_form_field(name))

    def _add_error(self, field, error):
        # if the error is from one of the processors, bind it to the field too
        field._error = error
        self._has_error = True

    def _run_processor(self, prefix, field_name, value):
        processor_name = prefix + field_name
        processor = getattr(self, processor_name, None)
        if callable(processor):
            return processor(value)
        return value

    def is_valid(self):
        """Perform full form validation over the initialized form. The method
        has the following side-effects:
          - in case errors are found, the form's `errors` container is going to
            be populated accordingly.
          - validated and processed values are going to be put into the
            `processed_data` dictionary.

        :returns:  boolean indication whether the form is valid or not
        """
        for field_name, field in self.fields.items():
            # run pre-processor on value, if defined
            try:
                field.processed_value = self._run_processor(
                    self._pre_processor_prefix,
                    field_name,
                    field.value
                )
            except ValidationError as exc:
                self._add_error(field, exc)
                continue
            # perform individual field validation
            if not field.is_valid():
                self._has_error = True
                continue
            # run post-processor on processed value, if defined
            try:
                field.processed_value = self._run_processor(
                    self._post_processor_prefix,
                    field_name,
                    field.processed_value
                )
            except ValidationError as exc:
                self._add_error(field, exc)
                continue
            # if field level validations passed, add the value to a dictionary
            # holding validated / processed data
            self.processed_data[field_name] = field.processed_value

        # run form level validation only if there were no field errors detected
        if not self._has_error:
            try:
                self.validate()
            except ValidationError as exc:
                exc.is_form = True
                self._add_error(self, exc)

        return not self._has_error

    def validate(self):
        """Perform form-level validation, which can check fields dependent on
        each other. The function is expected to be overridden by implementors
        in case form-level validation is needed, but it's optional. In case an
        error is found, a `ValidationError` exception should be raised by the
        function."""
        pass

    @property
    def error(self):
        if not self._error:
            return ''
        message = self.messages.get(self._error.message, self.generic_error)
        return message

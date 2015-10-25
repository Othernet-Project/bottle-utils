try:
    from bottle_utils.i18n import lazy_gettext as _
except ImportError:
    _ = lambda x: x

from .fields import DormantField, Field
from .exceptions import ValidationError


class Form(object):
    """
    Base form class to be subclassed. To define a new form subclass this
    class::

        class NewForm(Form):
            field1 = Field('Field 1')
            field2 = Field('Field 2', [Required])

    Forms support field pre- and post-procesors. These methods are named after
    the field names by prepending ``preprocess_`` and ``postprocess_``
    respectively. For example::

        class NewForm(Form):
            field1 = Field('Field 1')
            field2 = Field('Field 2', [Required])

            def preprocess_field1(self, value):
                return value.replace('this', 'that')

            def postprocess_field1(self, value):
                return value + 'done'

    Preprocessors can be defined for individual fields, and are ran before any
    validation happens over the field's data. Preprocessors are also allowed
    to raise ``ValidationError``, though their actual purpose is to perform
    some manipulation over the incoming data, before it is passed over to the
    validators. The return value of the preprocessor is the value that is going
    to be validated further.

    Postprocessors perform a similar purpose as preprocessors, except that they
    are invoked after field-level validation passes. Their return value is the
    value that is going to be the stored as cleaned / validated data.
    """

    #: Prefix to use for looking up preprocessors
    _pre_processor_prefix = 'preprocess_'

    #: Prefix to use for looking up postprocessors
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
    def field_errors(self):
        """
        Dictionary of all field error messages. This property maps the field
        names to error message maps. Field names are mapped to fields' messages
        property, which maps error type to actual message. This dictionary can
        also be used to modify the messages because message mappings are not
        copied.
        """
        messages = {}
        for field_name, field in self.fields.items():
            messages[field_name] = field.messages
        return messages

    #: Alias for :py:attr:`~field_errors` retained for
    # backwards-compatibility
    field_messages = field_errors

    @property
    def fields(self):
        """
        Dictionary of all the fields found on the form instance.  The return
        value is never cached so dynamically adding new fields to the form is
        allowed.
        """
        types = (Field, DormantField)
        is_form_field = lambda name: isinstance(getattr(self, name), types)
        ignored_attrs = ['fields', 'field_messages', 'field_errors']
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
        """
        Perform full form validation over the initialized form. The method
        has the following side-effects:

        - in case errors are found, the form's `errors` container is going to
          be populated accordingly.
        - validated and processed values are going to be put into the
          `processed_data` dictionary.

        Return value is a boolean, and is ``True`` is form data is valid.
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
        """
        Form-specific error message. This property evaluates to an empty string
        if form has no errors of its own.

        .. note::
            This property contains **only** form-specific errors, but no
            field errors. Field errors are available as the
            :py:attr:`~field_errors` property.
        """
        if not self._error:
            return ''
        message = self.messages.get(self._error.message, self.generic_error)
        return message

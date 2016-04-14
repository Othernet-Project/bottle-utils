# -*- coding: utf-8 -*-

"""
test_form.py: Unit tests for ``bottle_utils.form`` module

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from __future__ import unicode_literals

try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import bottle_utils.form as mod


class TestValidator(object):

    @mock.patch.object(mod.Validator, 'validate')
    def test_success(self, validate):
        validator = mod.Validator()
        try:
            validator('test')
        except Exception as exc:
            pytest.fail('Should not raise: {0}'.format(exc))

    @mock.patch.object(mod.Validator, 'validate')
    def test_fail(self, validate):
        err_msg = 'error message'
        validate.side_effect = mod.ValidationError(err_msg, {})
        validator = mod.Validator()
        with pytest.raises(mod.ValidationError):
            validator('test')

    def test_validator_message_override(self):
        """
        This is a regression test that verifies the message override provided
        via constructor argument won't affect the other instances or the class
        itself.
        """
        v1 = mod.Validator(messages={'foo': 'bar'})
        v2 = mod.Validator(messages={'bar': 'baz'})
        assert v1.messages != v2.messages
        assert mod.Validator.messages == {}


class TestField(object):

    def test_order(self):
        field1 = mod.Field()
        field2 = mod.Field()
        field3 = mod.Field()
        assert field1._order == 0
        assert field2._order == 1
        assert field3._order == 2

    def test_bind(self):
        class CustomField(mod.Field):
            def __init__(self, label, validators, something, **kwargs):
                self.something = something
                super(CustomField, self).__init__(label, validators, **kwargs)

        field1 = CustomField('label', validators=[], something='this')
        field2 = CustomField('label', validators=[], something='that')
        bound_field1 = field1.bind('field1')
        bound_field2 = field2.bind('field2')
        assert bound_field1.name == 'field1'
        assert bound_field2.name == 'field2'
        assert not bound_field1.is_value_bound
        assert not bound_field2.is_value_bound
        assert bound_field1.something == 'this'
        assert bound_field2.something == 'that'
        bound_field1.value = 'test'
        assert bound_field2.value is None

    def test_bind_value(self):
        field = mod.Field('test', name='alreadybound')
        field.bind_value('val')
        assert field.is_value_bound
        assert field.value == 'val'

    @mock.patch.object(mod.Field, 'parse')
    def test_is_valid_parse_fail(self, parse):
        value = 42
        parse.side_effect = ValueError('test')
        field = mod.Field('label', name='alreadybound')
        field.bind_value(value)
        assert not field.is_valid()
        assert isinstance(field._error, mod.ValidationError)
        assert field._error.message == 'generic'
        assert field._error.params == {'value': value}

    @mock.patch.object(mod.Field, 'parse')
    def test_is_valid_no_validators(self, parse):
        parse.side_effect = lambda x: x
        field = mod.Field('label', name='alreadybound')
        field.bind_value('test')
        assert field.is_valid()

    @mock.patch.object(mod.Field, 'parse')
    def test_is_valid_validator_success(self, parse):
        parse.side_effect = lambda x: x
        mocked_validator = mock.Mock()
        mocked_validator.messages = {}
        field = mod.Field('label',
                          name='alreadybound',
                          validators=[mocked_validator])
        field.bind_value('test')
        assert field.is_valid()
        mocked_validator.assert_called_once_with('test')

    @mock.patch.object(mod.Field, 'parse')
    def test_is_valid_validator_fail(self, parse):
        parse.side_effect = lambda x: x
        mocked_validator = mock.Mock()
        mocked_validator.messages = {}
        error = mod.ValidationError('failure', {})
        mocked_validator.side_effect = error
        field = mod.Field('label',
                          name='alreadybound',
                          validators=[mocked_validator])
        field.bind_value('test')
        assert not field.is_valid()
        mocked_validator.assert_called_once_with('test')
        assert field._error == error

    def test_field_collects_validator_messages(self):
        mocked_validator1 = mock.Mock()
        mocked_validator1.messages = {'foo': 'bar'}
        mocked_validator2 = mock.Mock()
        mocked_validator2.messages = {'bar': 'baz'}
        field = mod.Field('label',
                          name='field',
                          validators=[mocked_validator1, mocked_validator2])
        assert 'foo' in field.messages
        assert 'bar' in field.messages


class TestStringField(object):

    def test_parse(self):
        field = mod.StringField('label', name='alreadybound')
        assert field.parse(None) == ''
        assert field.parse(3) == '3'
        assert field.parse('str') == 'str'


class TestIntegerfield(object):

    def test_parse(self):
        field = mod.IntegerField(name='alreadybound')
        assert field.parse(None) is None
        assert field.parse('321') == 321
        with pytest.raises(ValueError):
            field.parse('str')


class TestBooleanFieldIntegration(object):

    def test_is_valid(self):
        field = mod.BooleanField('label', value='val', name='alreadybound')
        for val in (None, '', 'another', 'val'):
            field.bind_value(val)
            assert field.is_valid()

        field2 = mod.BooleanField('label',
                                  name='alreadybound',
                                  value='val',
                                  validators=[mod.Required()])
        field2.bind_value(None)
        assert not field2.is_valid()

        field2.bind_value('')
        assert not field2.is_valid()

        field2.bind_value('another')
        assert not field2.is_valid()

        field2.bind_value('val')
        assert field2.is_valid()


class TestSelectFieldIntegration(object):

    def test_is_valid(self):
        choices = (
            (None, '---'),
            (1, 'first'),
            (2, 'second')
        )
        field = mod.SelectField('label', name='alreadybound', choices=choices)

        field.bind_value(None)
        assert field.is_valid()

        field.bind_value('1')
        assert field.is_valid()

        field.bind_value('3')
        assert not field.is_valid()

        field2 = mod.SelectField('label',
                                 name='alreadybound',
                                 choices=choices,
                                 validators=[mod.Required()])

        field2.bind_value(None)
        assert not field2.is_valid()

        field2.bind_value('1')
        assert field2.is_valid()

        field2.bind_value('3')
        assert not field2.is_valid()


@pytest.fixture()
def form_cls():
    class FormCls(mod.Form):
        field1 = mod.Field('Field 1')
        field2 = mod.Field('Field 2')
        test = 'fake'
        again = 3
    return FormCls


class TestForm(object):

    @mock.patch.object(mod.Field, 'bind_value')
    @mock.patch.object(mod.DormantField, 'bind')
    def test__bind(self, bind, bind_value, form_cls):
        bind.side_effect = lambda x: x
        form = form_cls()
        assert form.field1 == 'field1'
        assert form.field2 == 'field2'

        mocked_field = mock.Mock()
        bind.side_effect = lambda x: mocked_field
        form = form_cls({'field1': 1, 'field2': 2})
        mocked_field.bind_value.assert_has_calls([mock.call(2), mock.call(1)],
                                                 any_order=True)

    def test_fields(self, form_cls):
        form = form_cls({})
        assert form.fields == {'field1': form.field1, 'field2': form.field2}

    def test_fields_order(self, form_cls):
        form = form_cls()
        fields = list(form.fields.items())
        assert fields[0][1].name == 'field1'
        assert fields[1][1].name == 'field2'

    def test_is_valid_success(self, form_cls):
        mocked_field = mock.Mock()
        mocked_field.value = 3
        preprocessor = mock.Mock()
        preprocessor.return_value = 'preprocessed'
        postprocessor = mock.Mock()
        postprocessor.return_value = 'postprocessed'

        form = form_cls({'field_name': 3})
        form.preprocess_field_name = preprocessor
        form.postprocess_field_name = postprocessor
        fields_dict = {'field_name': mocked_field}
        with mock.patch.object(mod.Form, 'fields', fields_dict):
            assert form.is_valid()

        preprocessor.assert_called_once_with(3)
        mocked_field.is_valid.assert_called_once_with()
        postprocessor.assert_called_once_with('preprocessed')
        assert form.processed_data['field_name'] == 'postprocessed'
        assert mocked_field.value == 3

    def test_is_valid_field_fail(self, form_cls):
        mocked_field = mock.Mock()
        mocked_field.value = 3
        error = mod.ValidationError('has error', {'value': 3})
        mocked_field._error = error
        mocked_field.is_valid.return_value = False
        form = form_cls({'field1': 3})
        fields_dict = {'field1': mocked_field}
        with mock.patch.object(mod.Form, 'fields', fields_dict):
            assert not form.is_valid()

        mocked_field.is_valid.assert_called_once_with()
        assert mocked_field._error == error

    def test_is_valid_preprocessor_fail(self, form_cls):
        preprocessor = mock.Mock()
        error = mod.ValidationError('failure', {'value': 3})
        preprocessor.side_effect = error

        mocked_field = mock.Mock()
        mocked_field.value = 3
        form = form_cls({'field_name': 3})
        form.preprocess_field1 = preprocessor

        fields_dict = {'field1': mocked_field}
        with mock.patch.object(mod.Form, 'fields', fields_dict):
            assert not form.is_valid()

        assert mocked_field._error == error
        assert not mocked_field.is_valid.called
        preprocessor.assert_called_once_with(3)

    def test_is_valid_postprocessor_fail(self, form_cls):
        postprocessor = mock.Mock()
        error = mod.ValidationError('failure', {'value': 3})
        postprocessor.side_effect = error

        mocked_field = mock.Mock()
        mocked_field.value = 3
        form = form_cls({'field1': 3})
        form.postprocess_field1 = postprocessor

        fields_dict = {'field1': mocked_field}
        with mock.patch.object(mod.Form, 'fields', fields_dict):
            assert not form.is_valid()

        assert mocked_field._error == error
        mocked_field.is_valid.assert_called_once_with()
        postprocessor.assert_called_once_with(3)

    @mock.patch.object(mod.Form, 'validate')
    def test_is_valid_form_level_validate_fails(self, validate, form_cls):
        error = mod.ValidationError('dependency issue', {})
        validate.side_effect = error
        form = form_cls({})

        with mock.patch.object(mod.Form, 'fields', {}):
            assert not form.is_valid()

        validate.assert_called_once_with()
        assert form._error == error

    def test_form_error_messages(self, form_cls):
        form = form_cls({})
        form.field1.messages = {'foo': 'bar'}
        form.field2.messages = {'bar': 'baz'}
        assert form.field_messages == {
            'field1': {'foo': 'bar'},
            'field2': {'bar': 'baz'},
        }


@mock.patch('bottle_utils.i18n.request')
def test_form_integration(request):

    class SomeForm(mod.Form):
        name = mod.StringField('Name', validators=[mod.Required()])
        age = mod.IntegerField('Age', validators=[mod.Required()])
        info = mod.StringField('Info')
        accept_terms = mod.BooleanField('Accept Terms',
                                        validators=[mod.Required()],
                                        value='terms_ok')

    form = SomeForm({})
    assert not form.is_valid()
    assert form.name.error
    assert form.age.error
    assert form.accept_terms.error
    assert not form.info.error

    form = SomeForm({'name': 'test', 'age': 99, 'accept_terms': 'terms_ok'})
    assert form.is_valid()
    assert form.processed_data == {'name': 'test',
                                   'age': 99,
                                   'info': '',
                                   'accept_terms': True}

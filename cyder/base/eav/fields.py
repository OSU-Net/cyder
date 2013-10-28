from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from south.modelsinspector import add_introspection_rules

from cyder.base.eav import validators
from cyder.base.eav.constants import (ATTRIBUTE_TYPES, ATTRIBUTE_INFORMATIONAL,
                                      ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT)


class AttributeValueTypeField(models.CharField):
    """
    This field represents the attribute value type -- in other words, the
    type of data the EAV value is allowed to hold. It names a validator defined
    in cyder.base.eav.validators, which is called in EAVValueField.validate
    with the value as its argument. Informational attributes are not validated,
    so this field's value is set to the empty string if the attribute is
    informational.

    Arguments:
        attribute_type_field: the name of the attribute_type field
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.attribute_type_field = kwargs.pop('attribute_type_field', None)
        if self.attribute_type_field is None:
            raise Exception("The 'attribute_type_field' argument is required")

        kwargs['blank'] = False # always run validate()

        super(AttributeValueTypeField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        attribute_type = getattr(model_instance, self.attribute_type_field)
        if attribute_type == ATTRIBUTE_INFORMATIONAL:
            # If the attribute is informational, we don't validate the value.
            value = u''

        return super(AttributeValueTypeField, self).clean(value,
                                                          model_instance)

    def validate(self, value, model_instance):
        attribute_type = getattr(model_instance, self.attribute_type_field)

        if attribute_type in (ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT):
            if not value:
                raise ValidationError('DHCP options and statements require a '
                                      'value type')
            elif not hasattr(validators, value):
                raise ValidationError("Invalid value type. The validator "
                                      "'{0}' does not exist" .format(value))

        # super(...).validate will choke if value is '' or u'', because
        # self.blank == False.
        if value:
            super(AttributeValueTypeField, self).validate(value,
                                                          model_instance)


class EAVValueField(models.CharField):
    """
    This field represents an EAV value. It strips leading and trailing
    whitespace and validates using the validator function specified in
    the EAV attribute object's attribute_type field.

    Arguments:
        attribute_field: the name of the attribute field
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.attribute_field = kwargs.pop('attribute_field', None)
        if self.attribute_field is None:
            raise Exception("The 'attribute_field' argument is required")

        super(EAVValueField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not isinstance(value, unicode):
            value = value.decode() # force it to unicode; assume ASCII

        value = value.strip()

        return super(EAVValueField, self).to_python(value)

    def validate(self, value, model_instance):
        if not getattr(model_instance, self.attribute_field + '_id'):
            return

        attribute = getattr(model_instance, self.attribute_field)

        if attribute.attribute_type in (ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT):
            try:
                value.encode('ascii') # ignore the return value
            except UnicodeEncodeError:
                raise ValidationError('DHCP option or statement value can '
                                      'only contain ASCII characters')

            validator = getattr(validators, attribute.value_type)
            validator(value)

        super(EAVValueField, self).validate(value, model_instance)


class EAVAttributeField(models.ForeignKey):
    """
    This field is almost identical to a ForeignKey except that the target model
    is always Attribute and that it takes a type_choices argument to simplify
    attribute_type filtering in the model and the UI.

    Arguments:
        type_choices: an iterable containing the attribute_type values that
                      specify allowable attributes
    """

    def __init__(self, *args, **kwargs):
        if 'type_choices' in kwargs:
            kwargs['limit_choices_to'] = \
                {'attribute_type__in': kwargs['type_choices']}

            self.type_choices = [
                (attr_type, dict(ATTRIBUTE_TYPES)[attr_type])
                for attr_type in kwargs.pop('type_choices')
            ]
        else:
            self.type_choices = ATTRIBUTE_TYPES

        super(EAVAttributeField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        return AttributeFormField(choices_query=self.rel.limit_choices_to,
                                  **kwargs)


class AttributeFormField(forms.CharField):
    """
    This field is the form field for EAVAttributeField; the user inputs a
    attribute name, and the field converts that to a reference to the actual
    Attribute object, raising a ValidationError if the attribute name is
    invalid.
    """

    def __init__(self, *args, **kwargs):
        if 'choices_query' in kwargs:
            self.choices_query = kwargs.pop('choices_query')
        else:
            raise Exception("The 'choices_query' argument is required")

        super(AttributeFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        from cyder.base.eav.models import Attribute

        try:
            return Attribute.objects.get(name=value, **self.choices_query)
        except Attribute.DoesNotExist:
            raise ValidationError("No such attribute")


# "Introspection rules" tell South which custom field arguments it needs to
# keep track of. Don't change them unless you know what you're doing.


add_introspection_rules(
    [
        (
            [AttributeValueTypeField], # model
            [], # args
            {'attribute_type_field': ('', {'is_value': True})} # kwargs
        ),
        (
            [EAVValueField], # model
            [], # args
            {'attribute_field': ('', {'is_value': True})} # kwargs
        ),
        (
            [EAVAttributeField], # model
            [], # args
            {} # kwargs
        )
    ],
    [
        r'^cyder\.base\.eav\.fields\.AttributeValueTypeField',
        r'^cyder\.base\.eav\.fields\.EAVValueField',
        r'^cyder\.base\.eav\.fields\.EAVAttributeField',
    ]
)

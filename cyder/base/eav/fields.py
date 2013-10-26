from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from south.modelsinspector import add_introspection_rules

from cyder.base.eav import validators
from cyder.base.eav.constants import (ATTRIBUTE_INFORMATIONAL,
                                      ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT)


class AttributeValueTypeField(models.CharField):
    __metaclass__ = models.SubfieldBase


    def __init__(self, *args, **kwargs):
        if 'attribute_type_field' in kwargs:
            self.attribute_type_field = kwargs.pop('attribute_type_field')
        else:
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

        if value:
            super(AttributeValueTypeField, self).validate(value,
                                                          model_instance)
        # super(...).validate will choke if value is '' or u'', because
        # self.blank == False.


class EAVValueField(models.CharField):
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
    def formfield(self, **kwargs):
        return AttributeFormField(choices=self.rel.limit_choices_to, **kwargs)


class AttributeFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if 'choices' in kwargs:
            self.choices = kwargs.pop('choices')
        else:
            raise Exception("The 'choices' argument is required")

        super(AttributeFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        from cyder.base.eav.models import Attribute

        try:
            return Attribute.objects.get(name=value, **self.choices)
        except Attribute.DoesNotExist:
            raise ValidationError("No such attribute")


add_introspection_rules([
    (
        [AttributeValueTypeField], # model
        [], # args
        {'attribute_type_field': ('attribute_type_field', {})}, # kwargs
    )
], [r'^cyder\.base\.eav\.fields\.AttributeValueTypeField'])


add_introspection_rules([
    (
        [EAVValueField], # model
        [], # args
        {'attribute_field': ('attribute_field', {})}, # kwargs
    )
], [r'^cyder\.base\.eav\.fields\.EAVValueField'])


add_introspection_rules([
    (
        [EAVAttributeField], # model
        [], # args
        {}, # kwargs
    )
], [r'^cyder\.base\.eav\.fields\.EAVAttributeField'])

from django.core.exceptions import ValidationError
from django.db import models

from cyder.base.eav import validators
from cyder.base.eav.constants import (ATTRIBUTE_TYPES, ATTRIBUTE_INFORMATIONAL,
                                      ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT)
from cyder.base.eav.fields import AttributeValueTypeField, EAVValueField
from cyder.base.eav.utils import is_hex_byte_sequence
from cyder.base.eav.validators import VALUE_TYPES
from cyder.base.mixins import ObjectUrlMixin


class Attribute(models.Model):
    class Meta:
        db_table = 'attribute'


    name = models.CharField(max_length=255)
    attribute_type = models.CharField(max_length=1, choices=ATTRIBUTE_TYPES)
    value_type = AttributeValueTypeField(max_length=20, choices=VALUE_TYPES,
                                  attribute_type_field='attribute_type')


    def __unicode__(self):
        return self.name


class EAVBase(models.Model, ObjectUrlMixin):
    """The entity-attribute-value base model

    When you inherit from this model, you must define the following field::
        attribute = ForeignKey(Attribute)

    You should define a ForeignKey field to the related object (the entity).
    Parts of the Cyder UI infer the relatedness from the field name, so make
    sure it follows the convention defined in cyder.base.views.get_update_form
    near the assignment of `form.fields[related_type]`, or else you'll get
    strange behavior.

    You should also specifiy `unique_together = (ENTITY, Attribute)` in `Meta`,
    where ENTITY is the name of the entity field.

    The child class is required to define the attribute field because it allows
    you to filter the attribute choices by adding
    :code:`limit_choices_to={'attribute_type': x}` or
    :code:`limit_choices_to={'attribute_type__in': x}` to the argument list.
    """

    class Meta:
        abstract = True


    value = EAVValueField(max_length=255, attribute_field='attribute')


    def __unicode__(self):
        kv_formats = {
            ATTRIBUTE_INFORMATIONAL: u'{0} = {1}',
            ATTRIBUTE_OPTION: u'option {0} {1}',
            ATTRIBUTE_STATEMENT: u'{0} {1}',
        }

        if self.attribute.value_type == 'string':
            add_quotes = not is_hex_byte_sequence(self.value)
        elif self.attribute.value_type == 'text':
            add_quotes = True
        else:
            add_quotes = False

        value = (u'"{0}"' if add_quotes else u'{0}').format(self.value)

        return (kv_formats[self.attribute.attribute_type]
                .format(self.attribute.name, value))


    def details(self):
        """For tables."""
        data = super(EAVBase, self).details()
        data['data'] = [
            ('Attribute', 'attribute__name', self.attribute),
            ('Value', 'value', self.value),
        ]
        return data

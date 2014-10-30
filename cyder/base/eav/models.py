from django.db import models

from cyder.base.eav.constants import (ATTRIBUTE_TYPES, ATTRIBUTE_INVENTORY,
                                      ATTRIBUTE_OPTION, ATTRIBUTE_STATEMENT)
from cyder.base.eav.fields import AttributeValueTypeField, EAVValueField
from cyder.base.eav.utils import is_hex_byte_sequence
from cyder.base.eav.validators import VALUE_TYPES
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import classproperty, safe_save


class Attribute(models.Model):
    search_fields = ('name',)

    class Meta:
        app_label = 'cyder'
        db_table = 'attribute'

    name = models.CharField(max_length=255)
    attribute_type = models.CharField(max_length=1, choices=ATTRIBUTE_TYPES)
    value_type = AttributeValueTypeField(max_length=20, choices=VALUE_TYPES,
                                         attribute_type_field='attribute_type')

    def __unicode__(self):
        return self.name


class EAVBase(BaseModel, ObjectUrlMixin):
    """The entity-attribute-value base model

    When you inherit from this model, you must define the following fields::
        entity = ForeignKey(ENTITY)
        attribute = EAVAttributeField(Attribute)
    where ENTITY is the entity model.

    If you define a custom Meta class on your model, ensure it inherits from
    :code:`EAVBase.Meta`.

    To restrict the attribute field by attribute type, pass EAVAttributeField
    the `type_choices` keyword argument with an iterable specifying the
    attribute types to allow.
    """

    class Meta:
        abstract = True
        unique_together = ('entity', 'attribute')

    def check_in_ctnr(self, ctnr):
        return ctnr.check_contains_obj(self.entity)

    @property
    def pretty_name(self):
        return self.attribute.name

    @classproperty
    @classmethod
    def pretty_type(cls):
        return cls._meta.get_field('entity').rel.to.pretty_type + ' attribute'

    value = EAVValueField(max_length=255, attribute_field='attribute')

    def __unicode__(self):
        kv_formats = {
            ATTRIBUTE_INVENTORY: u'{0} = {1}',
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

    @safe_save
    def save(self, *args, **kwargs):
        super(EAVBase, self).save(*args, **kwargs)

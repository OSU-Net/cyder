from django import forms
from django.db.models import CharField, NOT_PROVIDED, SubfieldBase
from django.core.exceptions import ValidationError
from south.modelsinspector import add_introspection_rules

from cyder.cydhcp.validation import validate_mac


class MacAddrField(CharField):
    """A general purpose MAC address field
    This field holds a MAC address. clean() removes colons and hyphens from the
    field value, raising an exception if the value is invalid or empty.

    Arguments:

    dhcp_enabled (string):
        The name of another attribute (possibly a field) in the model that
        holds a boolean specifying whether to validate this MacAddrField; if
        not specified, always validate.
    """

    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        self.dhcp_enabled = kwargs.pop('dhcp_enabled', True)

        kwargs['max_length'] = 17
        kwargs['blank'] = False  # always call MacAddrField.clean
        kwargs['null'] = True

        super(MacAddrField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value:
            return value.lower().replace(':', '').replace('-', '')
        else:
            return None

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact' and value == '':
            raise Exception(
                "When using the __exact lookup type, use a query value of "
                "None instead of ''. Even though get_prep_value transforms "
                "'' into None, Django only converts __exact queries into "
                "__isnull queries if the *user*-provided query value is None.")
        else:
            return super(MacAddrField, self).get_prep_lookup(
                lookup_type, value)

    def to_python(self, value):
        value = super(MacAddrField, self).to_python(value)

        if value:
            value = value.lower().replace(':', '').replace('-', '')
            value = reduce(lambda x,y: x + ':' + y,
                           (value[i:i+2] for i in xrange(0, 12, 2)))
        elif value == '':
            value = None
        return value

    def clean(self, value, model_instance):
        value_required = (self.dhcp_enabled is True
            or (isinstance(self.dhcp_enabled, basestring) and
                getattr(model_instance, self.dhcp_enabled)))

        if (value_required and not value):
            raise ValidationError(
                "This field is required when DHCP is enabled")

        if value:
            validate_mac(value)
            return super(MacAddrField, self).clean(value, model_instance)
        else:
            # If value is blank, CharField.clean will choke.
            return value

    def formfield(self, **kwargs):
        kwargs.update({
            'required': False,
            'max_length': self.max_length,
        })
        return forms.CharField(**kwargs)


add_introspection_rules([
    (
        [MacAddrField], # model
        [], # args
        {'dhcp_enabled': ('dhcp_enabled', {})}, # kwargs
    )
], [r'^cyder\.base\.fields\.MacAddrField'])

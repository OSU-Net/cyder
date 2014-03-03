from django.db.models import CharField, NOT_PROVIDED, SubfieldBase
from django.core.exceptions import ValidationError
from south.modelsinspector import add_introspection_rules

from cyder.cydhcp.validation import validate_mac


class MacAddrField(CharField):
    """A general purpose MAC address field
    This field holds a MAC address. clean() removes colons and hyphens from the
    field value, raising an exception if the value is invalid or empty.

    Arguments:

    dhcp_enabled (string): The name of another attribute (possibly a field) in
                           the model that holds a boolean specifying whether to
                           validate this MacAddrField; if not specified, always
                           validate.
    """

    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        if 'dhcp_enabled' in kwargs:
            self.dhcp_enabled = kwargs.pop('dhcp_enabled')
        else:
            self.dhcp_enabled = None # always validate

        kwargs['max_length'] = 17
        kwargs['blank'] = True

        super(MacAddrField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super(MacAddrField, self).get_prep_value(value)
        if value:
            value = value.lower().replace(':', '').replace('-', '')
        return value

    def to_python(self, value):
        value = super(MacAddrField, self).to_python(value)

        if value:
            value = value.lower().replace(':', '').replace('-', '')
            validate_mac(value)
            value = reduce(lambda x,y: x + ':' + y,
                           (value[i:i+2] for i in xrange(0, 12, 2)))
        return value

    def clean(self, value, model_instance):
        if ((not self.dhcp_enabled
                or getattr(model_instance, self.dhcp_enabled))
                and value == ''):
            raise ValidationError(
                "This field is required when DHCP is enabled")

        return super(MacAddrField, self).clean(value, model_instance)


add_introspection_rules([
    (
        [MacAddrField], # model
        [], # args
        {'dhcp_enabled': ('dhcp_enabled', {})}, # kwargs
    )
], [r'^cyder\.core\.fields\.MacAddrField'])

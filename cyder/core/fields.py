from django.db.models import CharField, NOT_PROVIDED
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

    def __init__(self, *args, **kwargs):
        if 'dhcp_enabled' in kwargs:
            self.dhcp_enabled = kwargs.pop('dhcp_enabled')
        else:
            self.dhcp_enabled = None # always validate

        kwargs['max_length'] = 12
        kwargs['blank'] = True

        super(MacAddrField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        # [   always validate   ]  [             DHCP is enabled              ]
        if not self.dhcp_enabled or getattr(model_instance, self.dhcp_enabled):
            if value == '':
                raise ValidationError(
                    "This field is required when DHCP is enabled")
            value = value.lower().replace(':', '')
            validate_mac(value)

        value = super(CharField, self).clean(value, model_instance)
        return value


add_introspection_rules([
    (
        [MacAddrField], # model
        [], # args
        {'dhcp_enabled': ('dhcp_enabled', {})}, # kwargs
    )
], [r'^cyder\.core\.fields\.MacAddrField'])

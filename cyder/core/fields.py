from django.db.models import CharField

from cyder.cydhcp.validation import validate_mac


class MacAddrField(CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' in kwargs:
            raise Exception("You cannot specify a max_length. max_length is "
                            "fixed at 12 for MacAddrFields.")
        kwargs['max_length'] = 12

        super(MacAddrField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        if self.blank and value == '':
            return value
        value = value.lower().replace(':', '')
        validate_mac(value)
        value = super(CharField, self).clean(value, model_instance)
        return value

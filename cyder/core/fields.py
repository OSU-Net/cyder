from django.db.models import CharField

from cyder.cydhcp.validation import validate_mac


class MacAddrField(CharField):
    def __init__(self, *args, **kwargs):
        super(MacAddrField, self).__init__(*args, max_length=12, **kwargs)

    def clean(self, value, model_instance):
        if value == '':
            return value
        value = value.lower().replace(':', '')
        validate_mac(value)
        value = super(CharField, self).clean(value, model_instance)
        return value

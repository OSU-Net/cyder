from django import forms
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.forms import DNSForm
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.forms import RangeWizard


class AddressRecordForm(DNSForm, RangeWizard, UsabilityFormMixin):
    def __init__(self, *args, **kwargs):
        super(AddressRecordForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['label', 'domain', 'vrf', 'site', 'range',
                                'ip_type', 'next_ip', 'ip_str', 'views', 'ttl',
                                'description']

    class Meta:
        model = AddressRecord
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain', 'fqdn')
        fields = ('label', 'domain', 'ip_type', 'ip_str', 'views', 'ttl',
                  'description')
        widgets = {'views': forms.CheckboxSelectMultiple,
                   'ip_type': forms.RadioSelect}


class AddressRecordFQDNForm(AddressRecordForm):
    class Meta:
        model = AddressRecord
        fields = ('fqdn', 'ip_type', 'ip_str', 'views', 'ttl', 'description')
        widgets = {'views': forms.CheckboxSelectMultiple,
                   'ip_type': forms.RadioSelect}

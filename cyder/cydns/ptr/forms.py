from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.ptr.models import PTR
from cyder.cydhcp.forms import RangeWizard
from cyder.base.mixins import UsabilityFormMixin


class PTRForm(DNSForm, RangeWizard, UsabilityFormMixin):

    def __init__(self, *args, **kwargs):
        super(PTRForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['label', 'domain', 'vrf', 'site', 'range',
                                'ip_type', 'next_ip', 'ip_str', 'views', 'ttl',
                                'description']

    def delete_instance(self, instance):
        instance.delete()

    class Meta:
        model = PTR
        exclude = ('ip', 'reverse_domain', 'ip_upper',
                   'ip_lower')
        widgets = {'views': forms.CheckboxSelectMultiple,
                   'ip_type': forms.RadioSelect}

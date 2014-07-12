from django import forms
from django.core.exceptions import ValidationError

import ipaddr

from cyder.base.eav.forms import get_eav_form
from cyder.base.mixins import UsabilityFormMixin
from cyder.core.system.models import System
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.forms import RangeWizard
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticInterfaceAV)
from cyder.cydhcp.range.models import Range
from cyder.cydns.view.models import View
from cyder.cydns.forms import ViewChoiceForm
from cyder.cydns.validation import validate_label


def validate_ip(ip):
    try:
        ipaddr.IPv4Address(ip)
    except ipaddr.AddressValueError:
        try:
            ipaddr.IPv6Address(ip)
        except ipaddr.AddressValueError:
            raise ValidationError("IP address not in valid form.")


class StaticInterfaceForm(RangeWizard, ViewChoiceForm,
                          UsabilityFormMixin):
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)
    label = forms.CharField(max_length=128, required=True, label="Hostname")
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(StaticInterfaceForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['system', 'description', 'label', 'domain',
                                'mac', 'vrf', 'site', 'range', 'ip_type',
                                'next_ip', 'ip_str', 'ttl', 'workgroup',
                                'expire', 'views', 'dhcp_enabled',
                                'dns_enabled', 'ctnr']
        self.fields['range'].queryset = Range.objects.filter(range_type=STATIC)

    class Meta:
        model = StaticInterface
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain', 'fqdn',
                   'last_seen')
        widgets = {'ip_type': forms.RadioSelect,
                   'views': forms.CheckboxSelectMultiple}
        always_validate = ('mac',)


StaticInterfaceAVForm = get_eav_form(StaticInterfaceAV, StaticInterface)


class FullStaticInterfaceForm(forms.ModelForm):
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = StaticInterface
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain',
                   'fqdn')

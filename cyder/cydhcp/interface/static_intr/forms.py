from django import forms
from django.core.exceptions import ValidationError

import ipaddr

from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import (StaticInterface,
                                                       StaticInterfaceAV)
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.validation import validate_mac
from cyder.cydns.view.models import View
from cyder.cydhcp.forms import RangeWizard
from cyder.cydns.validation import validate_label
from cyder.base.mixins import UsabilityFormMixin


def validate_ip(ip):
    try:
        ipaddr.IPv4Address(ip)
    except ipaddr.AddressValueError:
        try:
            ipaddr.IPv6Address(ip)
        except ipaddr.AddressValueError:
            raise ValidationError("IP address not in valid form.")


class CombineForm(forms.Form):
    mac = forms.CharField(validators=[validate_mac])
    system = forms.ModelChoiceField(queryset=System.objects.all())


class StaticInterfaceForm(RangeWizard, UsabilityFormMixin):
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)
    label = forms.CharField(max_length=128, required=True)

    def __init__(self, *args, **kwargs):
        super(StaticInterfaceForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['system', 'description', 'label', 'domain',
                                'mac', 'vrf', 'site', 'range', 'ip_type',
                                'next_ip', 'ip_str', 'ttl', 'workgroup',
                                'dhcp_enabled', 'dns_enabled', 'ctnr']

    class Meta:
        model = StaticInterface
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain', 'fqdn',
                   'last_seen')
        widgets = {'ip_type': forms.RadioSelect}


class StaticInterfaceAVForm(forms.ModelForm):
    static_interface = forms.ModelChoiceField(
        queryset=StaticInterface.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = StaticInterfaceAV
        exclude = ('is_option', 'is_statement', 'is_quoted')


class FullStaticInterfaceForm(forms.ModelForm):
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = StaticInterface
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain',
                   'fqdn')


class StaticInterfaceQuickForm(forms.Form):
    mac = forms.CharField(validators=[validate_mac])
    label = forms.CharField(validators=[validate_label])
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)

    range_choices = []
    ranges = Range.objects.all().select_related(depth=4).filter(
        network__vlan__id__isnull=False)
    ranges = sorted(ranges, key=lambda a: a.network.site is not None and
                    (a.network.site.get_full_name(), a.start_str))
    for r in ranges:
        range_choices.append((str(r.pk), r.display()))
    range = forms.ChoiceField(choices=range_choices)

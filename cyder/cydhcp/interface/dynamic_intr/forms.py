from django import forms
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.range.models import Range


class DynamicInterfaceForm(forms.ModelForm, UsabilityFormMixin):
    vrf = forms.ModelChoiceField(
        queryset=Vrf.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'wizard'}))
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'wizard'}))
    range = forms.ModelChoiceField(
        queryset=Range.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'wizard'}))

    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['system', 'domain', 'mac', 'vrf',
                                'site', 'range', 'workgroup', 'dhcp_enabled',
                                'dns_enabled', 'ctnr']

    class Meta:
        model = DynamicInterface
        exclude = ('last_seen')


class DynamicIntrKeyValueForm(forms.ModelForm):
    dynamic_interface = forms.ModelChoiceField(
        queryset=DynamicInterface.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = DynamicIntrKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted',)

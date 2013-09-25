from django import forms

from cyder.base.constants import IP_TYPES
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.range.models import Range


class IpSearchForm(forms.Form):
    ip_type = forms.ChoiceField(label='Address Type',
                                choices=IP_TYPES.items())
    search_ip = forms.CharField(label='IP Address or IP Network')


class RangeWizard(forms.ModelForm):
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
    next_ip = forms.ChoiceField(
        label='Select Free IPv4 IP?',
        choices=(('on', 'on'), ('False', 'False')),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'wizard'}))

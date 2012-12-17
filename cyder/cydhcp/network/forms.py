from django import forms
from django.core.exceptions import ValidationError

import ipaddr

from cyder.base.constants import IP_TYPES
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.vlan.models import Vlan
from cydns.ip.models import ipv6_to_longs


class NetworkForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        empty_label="(Defaults to parent's site.)",
        required=False,
        help_text='The site the network will be put into. '
                  'Defaults to parent network\'s site'
    )

    def __init__(self, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)
        self.fields['dhcpd_raw_include'].label = "DHCP Config Extras"
        self.fields['dhcpd_raw_include'].widget.attrs.update(
            {'cols': '80',
             'style':
             'display: none; width: 680px;'})

    class Meta:
        model = Network
        exclude = ('ip_upper', 'ip_lower', 'prefixlen')

    def clean(self):
        cleaned_data = super(NetworkForm, self).clean()
        network_str = cleaned_data.get('network_str', '')
        try:
            ip_type = cleaned_data.get('ip_type')
            if ip_type not in ('4', '6'):
                raise ValidationError("IP type must be either IPv4 or IPv6.")
            if ip_type == '4':
                network = ipaddr.IPv4Network(network_str)
                ip_upper, ip_lower = 0, int(network.network)
            elif ip_type == '6':
                network = ipaddr.IPv6Network(network_str)
                ip_upper, ip_lower = ipv6_to_longs(network.network)

        except ipaddr.AddressValueError, e:
            raise ValidationError("Bad Ip address {0}".format(e))
        except ipaddr.NetmaskValueError, e:
            raise ValidationError("Bad Netmask {0}".format(e))
        if (Network.objects.filter(ip_upper=ip_upper,
                  ip_lower=ip_lower).exists()):
            raise ValidationError("This network has already been allocated.")
        return cleaned_data


class NetworkForm_network(forms.Form):
    network = forms.CharField(
        required=True,
        help_text='Enter the address and mask in '
                 'CIDR notation (e.g. 10.0.0.0/24)')
    ip_type = forms.ChoiceField(choices=IP_TYPES.items())

    def clean(self):
        cleaned_data = super(NetworkForm_network, self).clean()
        network_str = cleaned_data.get('network', '')
        try:
            ip_type = cleaned_data.get('ip_type')
            if ip_type not in ('4', '6'):
                raise ValidationError("IP type must be either IPv4 or IPv6.")
            elif ip_type == '4':
                network = ipaddr.IPv4Network(network_str)
                ip_upper, ip_lower = 0, int(network.network)
            elif ip_type == '6':
                network = ipaddr.IPv6Network(network_str)
                ip_upper, ip_lower = ipv6_to_longs(network.network)
        except ipaddr.AddressValueError, e:
            raise ValidationError("Bad Ip address {0}".format(e))
        except ipaddr.NetmaskValueError, e:
            raise ValidationError("Bad Netmask {0}".format(e))
        if (Network.objects.filter(ip_upper=ip_upper,
                  ip_lower=ip_lower).exists()):
            raise ValidationError("This network has already been allocated.")
        # TODO add parent calculaitons
        return cleaned_data

class NetworkForm_site(forms.Form):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=True
    )

    def clean(self):
        cleaned_data = super(NetworkForm_site, self).clean()
        site = cleaned_data.get('site', None)
        if not site:
            raise ValidationError("That site does not exist.  Try again")
        return cleaned_data



class NetworkForm_vlan(forms.Form):
    vlan = forms.ModelChoiceField(
        queryset=Vlan.objects.all(),
        required=True,
    )
    name = forms.CharField()
    number = forms.IntegerField()
    create_choice = forms.ChoiceField(
        widget=forms.RadioSelect, initial='e', choices=(
            ('existing', 'Use existing VLAN template.'),
            ('new', 'Create New Vlan'),
            ('none', 'Don\'t assign a vlan'),
        ))

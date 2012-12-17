from django import forms

from cyder.base.constants import IP_TYPES


class IpSearchForm(forms.Form):
    ip_type = forms.ChoiceField(label='Address Type',
                                choices=IP_TYPES.items())
    search_ip = forms.CharField(label='IP Address or IP Network')

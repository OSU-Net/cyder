from django import forms

from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.cydhcp.network.models import Network


class RangeForm(forms.ModelForm):
    class Meta:
        model = Range
        exclude = ('start_upper', 'start_lower', 'end_upper', 'end_lower')

    def __init__(self, *args, **kwargs):
        super(RangeForm, self).__init__(*args, **kwargs)
        self.fields['network'].queryset = Network.objects.order_by(
            "network_str")
        self.fields['dhcpd_raw_include'].label = "DHCP Config Extras"
        self.fields['dhcpd_raw_include'].widget.attrs.update(
            {'cols': '80',
             'style': 'display: none;width: 680px'})


class RangeKeyValueForm(forms.ModelForm):
    class Meta:
        model = RangeKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted')

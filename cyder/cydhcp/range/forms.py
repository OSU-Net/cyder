from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.range.models import Range, RangeAV


class RangeForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Range
        widgets = {'range_type': forms.RadioSelect,
                   'ip_type': forms.RadioSelect}
        exclude = 'range_usage'

    def __init__(self, *args, **kwargs):
        super(RangeForm, self).__init__(*args, **kwargs)
        self.fields['dhcpd_raw_include'].label = "DHCP Config Extras"
        self.fields['dhcpd_raw_include'].widget.attrs.update(
            {'cols': '80',
             'style': 'display: none;width: 680px'})


RangeAVForm = get_eav_form(RangeAV, Range)

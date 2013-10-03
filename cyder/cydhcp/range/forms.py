from django import forms

from cyder.cydhcp.range.models import Range, RangeAV
from cyder.base.mixins import UsabilityFormMixin


class RangeForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Range
        widgets = {'range_type': forms.RadioSelect,
                   'ip_type': forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(RangeForm, self).__init__(*args, **kwargs)
        self.fields['dhcpd_raw_include'].label = "DHCP Config Extras"
        self.fields['dhcpd_raw_include'].widget.attrs.update(
            {'cols': '80',
             'style': 'display: none;width: 680px'})


class RangeAVForm(forms.ModelForm):
    range = forms.ModelChoiceField(
        queryset=Range.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = RangeAV
        exclude = ('is_option', 'is_statement', 'is_quoted')

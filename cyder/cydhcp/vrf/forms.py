from django import forms

from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue
from cyder.cydhcp.network.models import Network


class VrfForm(forms.ModelForm):
    class Meta:
        model = Vrf

    def __init__(self, *args, **kwargs):
        super(VrfForm, self).__init__(*args, **kwargs)
        self.fields['network'].queryset = Network.objects.order_by(
            "network_str")


class VrfKeyValueForm(forms.ModelForm):
    class Meta:
        model = VrfKeyValue
        exclude = ('is_quoted',)

from django import forms

from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue


class VrfForm(forms.ModelForm):
    class Meta:
        model = Vrf


class VrfKeyValueForm(forms.ModelForm):
    class Meta:
        model = VrfKeyValue
        exclude = ('is_quoted',)

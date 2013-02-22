from django import forms

from cyder.cydhcp.vrf.models import Vrf


class VrfForm(forms.ModelForm):
    class Meta:
        model = Vrf

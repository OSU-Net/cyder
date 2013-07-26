from django import forms

from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue
from cyder.base.mixins import UsabilityFormMixin


class VrfForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Vrf


class VrfKeyValueForm(forms.ModelForm):
    class Meta:
        model = VrfKeyValue
        exclude = ('is_quoted',)

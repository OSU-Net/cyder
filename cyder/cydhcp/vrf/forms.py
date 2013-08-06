from django import forms

from cyder.cydhcp.vrf.models import Vrf, VrfKeyValue
from cyder.base.mixins import AlphabetizeFormMixin


class VrfForm(forms.ModelForm, AlphabetizeFormMixin):
    class Meta:
        model = Vrf


class VrfKeyValueForm(forms.ModelForm):
    class Meta:
        model = VrfKeyValue
        exclude = ('is_quoted',)

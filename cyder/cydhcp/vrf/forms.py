from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.vrf.models import Vrf, VrfAV


class VrfForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Vrf


VrfAVForm = get_eav_form(VrfAV, Vrf)

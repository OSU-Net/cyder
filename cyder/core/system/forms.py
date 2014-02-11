from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.base.mixins import UsabilityFormMixin
from cyder.core.system.models import System, SystemAV


class SystemForm(forms.ModelForm):

    class Meta:
        model = System


class ExtendedSystemForm(forms.ModelForm, UsabilityFormMixin):
    interface_type = forms.ChoiceField(
        widget=forms.RadioSelect, choices=(
            ('static_interface', 'Static Interface'),
            ('dynamic_interface', 'Dynamic Interface')))

    class Meta:
        model = System


SystemAVForm = get_eav_form(SystemAV, System)

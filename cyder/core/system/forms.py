from django import forms

from cyder.core.system.models import System, SystemKeyValue
from cyder.base.mixins import UsabilityFormMixin


class SystemForm(forms.ModelForm):

    class Meta:
        model = System


class ExtendedSystemForm(forms.ModelForm, UsabilityFormMixin):
    interface_type = forms.ChoiceField(
        widget=forms.RadioSelect, choices=(
            ('Static', 'Static Interface'),
            ('Dynamic', 'Dynamic Interface')))

    class Meta:
        model = System


class SystemKeyValueForm(forms.ModelForm):
    system = forms.ModelChoiceField(
        queryset=System.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SystemKeyValue

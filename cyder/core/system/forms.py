from django.forms import ModelForm
from django import forms

from cyder.core.system.models import System, SystemKeyValue


class SystemForm(ModelForm):
    class Meta:
        model = System


class SystemKeyValueForm(ModelForm):
    system = forms.ModelChoiceField(
        queryset=System.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SystemKeyValue

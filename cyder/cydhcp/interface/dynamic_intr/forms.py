from django import forms
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)
from cyder.base.mixins import AlphabetizeFormMixin


class DynamicInterfaceForm(forms.ModelForm, AlphabetizeFormMixin):

    class Meta:
        model = DynamicInterface
        exclude = ('last_seen')


class DynamicIntrKeyValueForm(forms.ModelForm):
    dynamic_interface = forms.ModelChoiceField(
        queryset=DynamicInterface.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = DynamicIntrKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted',)

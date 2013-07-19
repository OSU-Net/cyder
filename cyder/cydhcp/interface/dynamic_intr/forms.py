from django import forms
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)
from cyder.base.mixins import AlphabetizeFormMixin


class DynamicInterfaceForm(forms.ModelForm, AlphabetizeFormMixin):

    class Meta:
        model = DynamicInterface


class DynamicIntrKeyValueForm(forms.ModelForm):

    class Meta:
        model = DynamicIntrKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted')

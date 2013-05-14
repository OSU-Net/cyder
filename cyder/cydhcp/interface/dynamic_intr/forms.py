from django import forms
from django.db import models
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)


class DynamicInterfaceForm(forms.ModelForm):

    class Meta:
        model = DynamicInterface


class DynamicIntrKeyValueForm(forms.ModelForm):

    class Meta:
        model = DynamicIntrKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted')

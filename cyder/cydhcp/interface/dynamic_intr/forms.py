from django import forms
from django.core.exceptions import ValidationError

import ipaddr

from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface

class DynamicInterfaceForm(forms.ModelForm):
    class Meta:
        model = DynamicInterface

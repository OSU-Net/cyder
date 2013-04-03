from django import forms
from django.db import models
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface


class DynamicInterfaceForm(forms.ModelForm):

    class Meta:
        model = DynamicInterface

from django import forms
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.supernet.models import Supernet


class SupernetForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Supernet
        exclude = ('start_lower', 'start_upper',
                   'end_lower', 'end_upper')
        widgets = {'ip_type': forms.RadioSelect,
                   'description': forms.Textarea}

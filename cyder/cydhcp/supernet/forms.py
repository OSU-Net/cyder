from django import forms
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.supernet.models import Supernet


class SupernetForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Supernet
        exclude = ('ip_upper', 'ip_lower', 'prefixlen')
        widgets = {'ip_type': forms.RadioSelect}

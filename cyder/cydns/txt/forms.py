from django.forms import ModelForm
from django import forms

from cyder.cydns.txt.models import TXT


class TXTForm(ModelForm):
    class Meta:
        model = TXT
        exclude = ('fqdn',)
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNTXTForm(ModelForm):
    class Meta:
        model = TXT
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

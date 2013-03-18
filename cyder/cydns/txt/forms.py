from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.txt.models import TXT


class TXTForm(DNSForm):
    class Meta:
        model = TXT
        exclude = ('fqdn',)
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNTXTForm(DNSForm):
    class Meta:
        model = TXT
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

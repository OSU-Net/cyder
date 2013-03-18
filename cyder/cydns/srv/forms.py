from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.srv.models import SRV


class SRVForm(DNSForm):
    class Meta:
        model = SRV
        exclude = ('fqdn',)
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNSRVForm(DNSForm):
    class Meta:
        model = SRV
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

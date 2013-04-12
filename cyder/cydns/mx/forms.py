from django import forms
from cyder.cydns.forms import DNSForm
from cyder.cydns.mx.models import MX


class MXForm(DNSForm):
    class Meta:
        model = MX
        exclude = ('fqdn',)
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNMXForm(MXForm):
    class Meta:
        model = MX
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

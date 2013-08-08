from django import forms
from cyder.cydns.forms import DNSForm
from cyder.cydns.mx.models import MX
from cyder.base.mixins import UsabilityFormMixin


class MXForm(DNSForm, UsabilityFormMixin):
    class Meta:
        model = MX
        exclude = ('fqdn',)
        fields = ('label', 'domain', 'server', 'priority', 'views', 'ttl',
                  'description')
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNMXForm(MXForm):
    class Meta:
        model = MX
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

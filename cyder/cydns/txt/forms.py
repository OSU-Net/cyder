from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.txt.models import TXT
from cyder.base.mixins import UsabilityFormMixin


class TXTForm(DNSForm, UsabilityFormMixin):
    class Meta:
        model = TXT
        exclude = ('fqdn',)
        fields = ('label', 'domain', 'txt_data', 'views', 'ttl',
                  'description', 'ctnr')
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNTXTForm(DNSForm):
    class Meta:
        model = TXT
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

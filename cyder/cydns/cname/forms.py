from django import forms

from cyder.cydns.cname.models import CNAME
from cyder.cydns.forms import DNSForm


class CNAMEForm(DNSForm):

    class Meta:
        model = CNAME
        exclude = ('target_domain', 'fqdn')
        fields = ('label', 'domain', 'target', 'views', 'ttl', 'description')
        widgets = {'views': forms.CheckboxSelectMultiple}
        # https://code.djangoproject.com/ticket/9321


class CNAMEFQDNForm(DNSForm):

    class Meta:
        model = CNAME
        fields = ('fqdn', 'target', 'views', 'ttl', 'description')
        widgets = {'views': forms.CheckboxSelectMultiple}
        # https://code.djangoproject.com/ticket/9321

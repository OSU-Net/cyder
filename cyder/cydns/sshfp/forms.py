from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.sshfp.models import SSHFP


class SSHFPForm(DNSForm):
    class Meta:
        model = SSHFP
        exclude = ('fqdn',)
        widgets = {'views': forms.CheckboxSelectMultiple}


class FQDNSSHFPForm(DNSForm):
    class Meta:
        model = SSHFP
        exclude = ('label', 'domain')
        widgets = {'views': forms.CheckboxSelectMultiple}

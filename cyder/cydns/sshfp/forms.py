from django.forms import ModelForm

from cyder.cydns.sshfp.models import SSHFP


class SSHFPForm(ModelForm):
    class Meta:
        model = SSHFP
        exclude = ('fqdn',)


class FQDNSSHFPForm(ModelForm):
    class Meta:
        model = SSHFP
        exclude = ('label', 'domain')

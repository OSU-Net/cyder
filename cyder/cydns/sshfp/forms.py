from cyder.cydns.forms import DNSForm
from cyder.cydns.sshfp.models import SSHFP


class SSHFPForm(DNSForm):
    class Meta:
        model = SSHFP
        exclude = ('fqdn',)


class FQDNSSHFPForm(DNSForm):
    class Meta:
        model = SSHFP
        exclude = ('label', 'domain')

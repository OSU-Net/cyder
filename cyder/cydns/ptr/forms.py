from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.ptr.models import PTR
from cyder.base.mixins import UsabilityFormMixin


class PTRForm(DNSForm, UsabilityFormMixin):
    def delete_instance(self, instance):
        instance.delete()

    class Meta:
        model = PTR
        exclude = ('ip', 'reverse_domain', 'ip_upper',
                   'ip_lower')
        fields = ('label', 'domain', 'ip_type', 'ip_str', 'views', 'ttl',
                  'description')
        widgets = {'views': forms.CheckboxSelectMultiple,
                   'ip_type': forms.RadioSelect}

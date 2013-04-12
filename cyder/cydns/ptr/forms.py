from django import forms

from cyder.cydns.forms import DNSForm
from cyder.cydns.ptr.models import PTR


class PTRForm(DNSForm):
    def delete_instance(self, instance):
        instance.delete()

    class Meta:
        model = PTR
        exclude = ('ip', 'reverse_domain', 'ip_upper',
                   'ip_lower')
        widgets = {'views': forms.CheckboxSelectMultiple}

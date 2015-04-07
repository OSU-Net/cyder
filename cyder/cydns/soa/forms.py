from django.forms import ModelForm
from cyder.base.mixins import UsabilityFormMixin
from cyder.base.eav.forms import get_eav_form
from cyder.cydns.soa.models import SOA, SOAAV


class SOAForm(ModelForm, UsabilityFormMixin):
    class Meta:
        model = SOA
        fields = ('root_domain', 'primary', 'contact', 'expire',
                  'retry', 'refresh', 'minimum', 'ttl', 'description',
                  'is_signed', 'dns_enabled')
        exclude = ('serial', 'dirty',)

    def clean(self, *args, **kwargs):
        contact = self.cleaned_data['contact']
        self.cleaned_data['contact'] = contact.replace('@', '.')
        return super(SOAForm, self).clean(*args, **kwargs)


SOAAVForm = get_eav_form(SOAAV, SOA)

from django.forms import ModelForm
from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.cydns.soa.models import SOA, SOAAV


class SOAForm(ModelForm):
    class Meta:
        model = SOA
        fields = ('description', 'primary', 'contact', 'expire', 'retry',
                  'refresh', 'minimum', 'ttl', 'is_signed')
        exclude = ('serial', 'dirty',)


SOAAVForm = get_eav_form(SOAAV, SOA)

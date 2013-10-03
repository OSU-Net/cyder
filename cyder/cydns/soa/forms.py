from django.forms import ModelForm
from django import forms
from cyder.cydns.soa.models import SOA, SOAKeyValue


class SOAForm(ModelForm):
    class Meta:
        model = SOA
        fields = ('primary', 'contact', 'expire', 'retry', 'refresh',
                  'minimum', 'ttl', 'description', 'is_signed', 'dns_enabled')
        exclude = ('serial', 'dirty',)


class SOAKeyValueForm(ModelForm):
    soa = forms.ModelChoiceField(
        queryset=SOA.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SOAKeyValue
        exclude = ('serial', 'dirty',)

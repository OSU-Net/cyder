from django.forms import ModelForm
from django import forms
from cyder.cydns.soa.models import SOA, SOAAV


class SOAForm(ModelForm):
    class Meta:
        model = SOA
        fields = ('description', 'primary', 'contact', 'expire', 'retry',
                  'refresh', 'minimum', 'ttl', 'is_signed')
        exclude = ('serial', 'dirty',)


class SOAAVForm(ModelForm):
    soa = forms.ModelChoiceField(
        queryset=SOA.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SOAAV
        exclude = ('serial', 'dirty',)

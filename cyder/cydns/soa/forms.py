from django.forms import ModelForm
from django import forms
from cyder.cydns.soa.models import SOA, SOAKeyValue


class SOAForm(ModelForm):
    class Meta:
        model = SOA
        exclude = ('serial', 'dirty',)


class SOAKeyValueForm(ModelForm):
    obj = forms.ModelChoiceField(
        queryset=SOA.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SOAKeyValue
        exclude = ('serial', 'dirty',)

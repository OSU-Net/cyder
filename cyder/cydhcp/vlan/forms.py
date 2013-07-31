from django import forms

from cyder.cydhcp.vlan.models import Vlan, VlanKeyValue


class VlanForm(forms.ModelForm):
    #site = forms.ModelChoiceField(queryset=Site.objects.all())

    class Meta:
        model = Vlan


class VlanKeyValueForm(forms.ModelForm):
    vlan = forms.ModelChoiceField(
            queryset=Vlan.objects.all(),
            widget=forms.HiddenInput())

    class Meta:
        model = VlanKeyValue
        exclude = ('is_quoted',)

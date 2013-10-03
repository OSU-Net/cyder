from django import forms

from cyder.cydhcp.vlan.models import Vlan, VlanAV


class VlanForm(forms.ModelForm):
    #site = forms.ModelChoiceField(queryset=Site.objects.all())

    class Meta:
        model = Vlan


class VlanAVForm(forms.ModelForm):
    vlan = forms.ModelChoiceField(
            queryset=Vlan.objects.all(),
            widget=forms.HiddenInput())

    class Meta:
        model = VlanAV
        exclude = ('is_quoted',)

from django import forms
from cyder.cydhcp.site.models import Site, SiteAV


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site


class SiteAVForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SiteAV
        exclude = ('is_quoted',)

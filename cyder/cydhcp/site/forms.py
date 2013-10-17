from django import forms
from cyder.cydhcp.site.models import Site, SiteAV


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site


class SiteAVForm(forms.ModelForm):
    entity = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = SiteAV
        fields = ('entity', 'attribute', 'value')

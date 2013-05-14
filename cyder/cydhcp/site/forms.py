from django import forms
from cyder.cydhcp.site.models import Site, SiteKeyValue


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site


class SiteKeyValueForm(forms.ModelForm):

    class Meta:
        model = SiteKeyValue
        exclude = ('is_quoted',)


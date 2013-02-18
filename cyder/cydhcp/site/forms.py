from django import forms
from cyder.cydhcp.site.models import Site


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site

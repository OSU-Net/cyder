from django import forms

from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site

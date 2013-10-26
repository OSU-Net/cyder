from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.cydhcp.site.models import Site, SiteAV


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site


SiteAVForm = get_eav_form(SiteAV, Site)

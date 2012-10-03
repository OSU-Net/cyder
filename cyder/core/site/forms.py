from django import forms

from cyder.core.site.models import Site
from cyder.core.network.models import Network


class SiteForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Site

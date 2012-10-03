from django import forms

from cyder.core.site.models import Site
from cyder.core.vlan.models import Vlan


class VlanForm(forms.ModelForm):
    #site = forms.ModelChoiceField(queryset=Site.objects.all())

    class Meta:
        model = Vlan

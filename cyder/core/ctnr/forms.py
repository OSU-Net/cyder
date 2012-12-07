from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr, CtnrUser


class CtnrForm(forms.ModelForm):
    class Meta:
        model = Ctnr


class CtnrUserForm(forms.ModelForm):
    level = forms.ChoiceField(widget=forms.RadioSelect, choices=LEVELS.items())

    class Meta:
        model = CtnrUser
        widgets = {
            'user': forms.Textarea(
                attrs={'id': 'user-searchbox', 'col': 80, 'rows': 1}),
            'ctnr': forms.HiddenInput(),
        }

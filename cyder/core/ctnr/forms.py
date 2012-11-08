from django import forms

from cyder.core.ctnr.models import Ctnr, CtnrUser


class CtnrForm(forms.ModelForm):
    class Meta:
        model = Ctnr


class CtnrUserForm(forms.ModelForm):
    level_choices = (
        (0, 'Guest'),
        (1, 'User'),
        (2, 'Admin'),
    )
    level = forms.ChoiceField(widget=forms.RadioSelect, choices=level_choices)

    class Meta:
        model = CtnrUser

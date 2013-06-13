from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr, CtnrUser


class CtnrForm(forms.ModelForm):
    class Meta:
        model = Ctnr
        exclude = ('users',)

class CtnrUserForm(forms.ModelForm):
    level = forms.ChoiceField(widget=forms.RadioSelect,
                              choices=[item for item in LEVELS.items()])

    class Meta:
        model = CtnrUser
        widgets = {
            'user': forms.TextInput(attrs={'id': 'user-searchbox'}),
            'ctnr': forms.HiddenInput(),
        }

from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.base.mixins import AlphabetizeFormMixin


class CtnrForm(forms.ModelForm, AlphabetizeFormMixin):
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

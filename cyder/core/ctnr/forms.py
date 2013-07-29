from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.base.mixins import UsabilityFormMixin


class CtnrForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Ctnr
        exclude = ('users',)

    def filter_by_ctnr_all(self, ctnr):
        pass


class CtnrUserForm(forms.ModelForm):
    level = forms.ChoiceField(widget=forms.RadioSelect,
                              choices=[item for item in LEVELS.items()])

    class Meta:
        model = CtnrUser
        widgets = {
            'user': forms.TextInput(attrs={'id': 'user-searchbox'}),
            'ctnr': forms.HiddenInput(),
        }

from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr
from cyder.base.mixins import AlphabetizeFormMixin


class CtnrForm(forms.ModelForm, AlphabetizeFormMixin):
    class Meta:
        model = Ctnr
        exclude = ('users',)


class CtnrUserForm(forms.Form):
    level = forms.ChoiceField(widget=forms.RadioSelect,
                              choices=[item for item in LEVELS.items()])


class CtnrObjectForm(forms.Form):
    obj_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        label='Type',
        choices=(
            ('user', 'User'),
            ('domain', 'Domain'),
            ('range', 'Range'),
            ('workgroup', 'Workgroup')))

    obj = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'object-searchbox'}),
        label='Search')

from django import forms

from cyder.base.constants import LEVELS
from cyder.base.mixins import UsabilityFormMixin
from cyder.core.ctnr.models import Ctnr


class CtnrForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Ctnr
        exclude = ('users',)

    def filter_by_ctnr_all(self, ctnr):
        pass


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

    def __init__(self, *args, **kwargs):
        obj_perm = kwargs.pop('obj_perm', False)
        super(CtnrObjectForm, self).__init__(*args, **kwargs)
        if not obj_perm:
            self.fields['obj_type'].choices = (('user', 'User'),)

    obj = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'object-searchbox'}),
        label='Search')

from django import forms

from cyder.base.constants import LEVELS
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.range.models import Range


class CtnrForm(forms.ModelForm):
    class Meta:
        model = Ctnr
        exclude = ('users',)

    def __init__(self, *args, **kwargs):
        super(CtnrForm, self).__init__(*args, **kwargs)
        self.fields['domains'].queryset = Domain.objects.order_by("name")
        self.fields['ranges'].queryset = Range.objects.order_by(
            "start_str", "end_str")


class CtnrUserForm(forms.ModelForm):
    level = forms.ChoiceField(widget=forms.RadioSelect,
                              choices=[item for item in LEVELS.items()])

    class Meta:
        model = CtnrUser
        widgets = {
            'user': forms.TextInput(attrs={'id': 'user-searchbox'}),
            'ctnr': forms.HiddenInput(),
        }

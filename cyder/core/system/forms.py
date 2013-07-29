from django import forms

from cyder.core.system.models import System


class SystemForm(forms.ModelForm):
    interface_type = forms.ChoiceField(
        widget=forms.RadioSelect, choices=(
            ('Static', 'Static Interface'),
            ('Dynamic', 'Dynamic Interface')))

    class Meta:
        model = System

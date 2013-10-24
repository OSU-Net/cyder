from django import forms
from cyder.base.eav.models import Attribute


def get_eav_form(eav_model, entity_model):
    class EAVForm(forms.ModelForm):
        entity = forms.ModelChoiceField(
            queryset=entity_model.objects.all(),
            widget=forms.HiddenInput())

        attribute = forms.ModelChoiceField(
            queryset=Attribute.objects.all(),
            widget=forms.TextInput())

        class Meta:
            model = eav_model
            fields = ('entity', 'attribute', 'value')

    return EAVForm

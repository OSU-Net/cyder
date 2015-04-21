from django import forms
from django.core.exceptions import ValidationError

from cyder.base.eav.constants import ATTRIBUTE_TYPES
from cyder.base.eav.models import Attribute


def get_eav_form(eav_model, entity_model):
    class EAVForm(forms.ModelForm):
        entity = forms.ModelChoiceField(
            queryset=entity_model.objects.all(),
            widget=forms.HiddenInput())

        class Meta:
            model = eav_model
            fields = ('entity', 'attribute', 'value')

    EAVForm.__name__ = eav_model.__name__ + 'Form'

    return EAVForm

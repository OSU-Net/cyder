from django import forms
from django.core.exceptions import ValidationError

from cyder.base.eav.constants import ATTRIBUTE_TYPES
from cyder.base.eav.models import Attribute


def get_eav_form(eav_model, entity_model):
    class EAVForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            if 'instance' in kwargs and kwargs['instance'] is not None:
                # This is a bound form with a real instance

                if 'initial' not in kwargs:
                    kwargs['initial'] = dict()

                # Set the attribute field to the name, not the pk
                kwargs['initial']['attribute'] = \
                    kwargs['instance'].attribute.name

                # Set the attribute_type field to the current attribute's type
                kwargs['initial']['attribute_type'] = \
                    kwargs['instance'].attribute.attribute_type

            super(EAVForm, self).__init__(*args, **kwargs)

        attribute_type = forms.ChoiceField(
            choices=eav_model._meta.get_field('attribute').type_choices)

        entity = forms.ModelChoiceField(
            queryset=entity_model.objects.all(),
            widget=forms.HiddenInput())

        class Meta:
            model = eav_model
            fields = ('entity', 'attribute_type', 'attribute', 'value')

    EAVForm.__name__ = eav_model.__name__ + 'Form'

    return EAVForm

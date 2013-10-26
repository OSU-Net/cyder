from django import forms
from django.core.exceptions import ValidationError

from cyder.base.eav.models import Attribute


class AttributeFormField(forms.CharField):
    def to_python(self, value):
        try:
            return Attribute.objects.get(
                name=value)
        except Attribute.DoesNotExist:
            raise ValidationError("No such attribute")


def get_eav_form(eav_model, entity_model):
    class EAVForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            if 'initial' not in kwargs:
                kwargs['initial'] = dict()
            kwargs['initial']['attribute'] = kwargs['instance'].attribute.name

            super(EAVForm, self).__init__(*args, **kwargs)

        entity = forms.ModelChoiceField(
            queryset=entity_model.objects.all(),
            widget=forms.HiddenInput())

        attribute = AttributeFormField()

        class Meta:
            model = eav_model
            fields = ('entity', 'attribute', 'value')

    return EAVForm

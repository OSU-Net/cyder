from django import forms


def get_eav_form(eav_model, entity_model):
    class EAVForm(forms.ModelForm):
        entity = forms.ModelChoiceField(
            queryset=entity_model.objects.all(),
            widget=forms.HiddenInput())

        class Meta:
            model = eav_model
            fields = ('entity', 'attribute', 'value')

    return EAVForm

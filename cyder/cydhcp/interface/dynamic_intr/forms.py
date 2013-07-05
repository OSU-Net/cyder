from django import forms
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicIntrKeyValue)
from cyder.cydhcp.range.models import Range
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydns.domain.models import Domain


class DynamicInterfaceForm(forms.ModelForm):

    class Meta:
        model = DynamicInterface

    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ctnr'].queryset = Ctnr.objects.order_by("name")
        self.fields['range'].queryset = Range.objects.order_by(
            "start_str", "end_str")
        self.fields['system'].queryset = System.objects.order_by("name")
        self.fields['domain'].queryset = Domain.objects.order_by("name")


class DynamicIntrKeyValueForm(forms.ModelForm):

    class Meta:
        model = DynamicIntrKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted')

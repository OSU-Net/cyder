from django import forms

from cyder.base.eav.forms import get_eav_form
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.forms import RangeWizard
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicInterfaceAV)
from cyder.cydhcp.range.models import Range


class DynamicInterfaceForm(RangeWizard, UsabilityFormMixin):
    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['system', 'mac', 'vrf', 'site',
                                'range', 'workgroup', 'dhcp_enabled', 'ctnr']
        self.fields['range'].required = True
        self.fields['range'].queryset = Range.objects.filter(
            range_type='dy')

    class Meta:
        model = DynamicInterface
        exclude = ('last_seen')


DynamicInterfaceAVForm = get_eav_form(DynamicInterfaceAV, DynamicInterface)

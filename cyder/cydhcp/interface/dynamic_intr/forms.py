from cyder.base.eav.forms import get_eav_form
from cyder.cydhcp.constants import DYNAMIC
from cyder.base.mixins import UsabilityFormMixin
from cyder.cydhcp.forms import RangeWizard
from cyder.cydhcp.interface.dynamic_intr.models import (DynamicInterface,
                                                        DynamicInterfaceAV)
from cyder.cydhcp.range.models import Range


class DynamicInterfaceForm(RangeWizard, UsabilityFormMixin):
    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['system', 'mac', 'vrf', 'site', 'range',
                                'workgroup', 'expire', 'dhcp_enabled', 'ctnr']
        self.fields['expire'].widget.format = "%d/%m/%Y"
        self.fields['range'].required = True
        self.fields['range'].queryset = Range.objects.filter(
            range_type=DYNAMIC)

    class Meta:
        model = DynamicInterface
        exclude = ('last_seen',)
        always_validate = ('mac',)


DynamicInterfaceAVForm = get_eav_form(DynamicInterfaceAV, DynamicInterface)

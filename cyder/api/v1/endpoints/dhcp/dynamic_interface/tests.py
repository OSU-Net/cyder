from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain


class DynamicInterfaceBase(DHCPAPITests):
    model = DynamicInterface
    urlname = "dynamic_interface"
    keyvalue_attr = "dynamicintrkeyvalue_set"

    def __init__(self, *args, **kwargs):
        Domain.objects.get_or_create(name='arpa')
        self.ctnr, _ = Ctnr.objects.get_or_create(name="TestCtnr")
        self.system, _ = System.objects.get_or_create(name="TestSystem")
        super(DynamicInterfaceBase, self).__init__(self, *args, **kwargs)

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
            'range': self.range,
            'system': self.system,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj


class DynamicInterfaceV4API_Test(DynamicInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceV4API_Test, self).__init__(self, *args, **kwargs)
        self.range, _ = Range.objects.get_or_create(
            start_str="12.12.0.0", end_str="12.12.255.255",
            is_reserved=True)


class DynamicInterfaceV6API_Test(DynamicInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(DynamicInterfaceV6API_Test, self).__init__(self, *args, **kwargs)
        self.range, _ = Range.objects.get_or_create(
            start_str="2001:0db8:0000:0000:0000:0000:0000:0000",
            end_str="2001:0db8:0000:0000:0000:0000:0000:0001",
            ip_type = '6', is_reserved=True)

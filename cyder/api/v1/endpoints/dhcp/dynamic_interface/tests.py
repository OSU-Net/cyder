from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.range.models import Range
from cyder.api.v1.tests.base import APITests


class DynamicInterfaceBase(APITests):
    model = DynamicInterface

    def setUp(self):
        self.ctnr, _ = Ctnr.objects.get_or_create(name="TestCtnr")
        self.system, _ = System.objects.get_or_create(name="TestSystem")
        super(DynamicInterfaceBase, self).setUp()

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
            'range': self.range,
            'system': self.system,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj


class DynamicInterfaceV4API_Test(DynamicInterfaceBase):
    __test__ = True

    def setUp(self):
        super(DynamicInterfaceV4API_Test, self).setUp()
        self.range, _ = Range.objects.get_or_create(
            start_str="12.12.0.0", end_str="12.12.255.255",
            is_reserved=True)


class DynamicInterfaceV6API_Test(DynamicInterfaceBase):
    __test__ = True

    def setUp(self):
        super(DynamicInterfaceV6API_Test, self).setUp()
        self.range, _ = Range.objects.get_or_create(
            start_str="2001:0db8:0000:0000:0000:0000:0000:0000",
            end_str="2001:0db8:0000:0000:0000:0000:0000:0001",
            ip_type='6', is_reserved=True)

from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.api.v1.tests.base import APITests
from cyder.cydhcp.constants import DYNAMIC


class DynamicInterfaceBase(APITests):
    model = DynamicInterface

    def setUp(self):
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
        self.network, _ = Network.objects.get_or_create(
            network_str="12.12.0.0/16")
        self.range, _ = Range.objects.get_or_create(
            start_str="12.12.0.1", end_str="12.12.255.254",
            range_type=DYNAMIC, is_reserved=True, domain=self.domain,
            network=self.network)


class DynamicInterfaceV6API_Test(DynamicInterfaceBase):
    __test__ = True

    def setUp(self):
        super(DynamicInterfaceV6API_Test, self).setUp()
        self.network, _ = Network.objects.get_or_create(
            ip_type='6', network_str="2001:db8:0:0:0:0:0:0/126")
        self.range, _ = Range.objects.get_or_create(
            start_str="2001:0db8:0000:0000:0000:0000:0000:0001",
            end_str="2001:0db8:0000:0000:0000:0000:0000:0002",
            ip_type='6', range_type=DYNAMIC, is_reserved=True,
            domain=self.domain, network=self.network)

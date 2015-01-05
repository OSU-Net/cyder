from cyder.core.system.models import System
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.api.v1.tests.base import APITests
from cyder.cydhcp.constants import DYNAMIC


class DynamicInterfaceV4API_Test(APITests):
    __test__ = True
    model = DynamicInterface

    def create_data(self):
        network = Network.objects.create(network_str="12.12.0.0/16")
        range = Range.objects.create(
            start_str="12.12.0.1", end_str="12.12.255.254", range_type=DYNAMIC,
            is_reserved=True, domain=self.domain, network=network)
        system = System.objects.create(name="TestSystem")

        return DynamicInterface.objects.create(
            ctnr=self.ctnr, mac='be:ef:fa:ce:f0:0d', range=range,
            system=system)


class DynamicInterfaceV6API_Test(APITests):
    __test__ = True
    model = DynamicInterface

    def create_data(self):
        network = Network.objects.create(
            ip_type='6', network_str="2001:db8:0:0:0:0:0:0/126")
        range = Range.objects.create(
            start_str="2001:0db8:0000:0000:0000:0000:0000:0001",
            end_str="2001:0db8:0000:0000:0000:0000:0000:0002", ip_type='6',
            range_type=DYNAMIC, is_reserved=True, domain=self.domain,
            network=network)
        system = System.objects.create(name="TestSystem")

        return DynamicInterface.objects.create(
            ctnr=self.ctnr, mac='be:ef:fa:ce:f0:0d', range=range,
            system=system)

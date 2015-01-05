from cyder.cydhcp.vlan.models import Vlan
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class VlanAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Vlan

    def create_data(self):
        return Vlan.objects.create(name='vlan', number=420)

from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.cydhcp.vlan.models import Vlan


class VlanAPI_Test(DHCPAPITests):
    model = Vlan

    def create_data(self):
        data = {
            'name': 'vlan',
            'number': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj


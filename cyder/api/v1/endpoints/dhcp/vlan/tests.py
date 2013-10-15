from cyder.cydhcp.vlan.models import Vlan
from cyder.api.v1.tests.base import APITests


class VlanAPI_Test(APITests):
    __test__ = True
    model = Vlan

    def create_data(self):
        data = {
            'name': 'vlan',
            'number': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

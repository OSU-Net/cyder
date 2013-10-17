from cyder.cydhcp.vrf.models import Vrf
from cyder.api.v1.tests.base import APITests


class VrfAPI_Test(APITests):
    __test__ = True
    model = Vrf

    def create_data(self):
        return self.model.objects.get_or_create(name='vrf')[0]

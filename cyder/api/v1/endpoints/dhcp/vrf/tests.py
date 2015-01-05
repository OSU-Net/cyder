from cyder.cydhcp.vrf.models import Vrf
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class VrfAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Vrf

    def create_data(self):
        return Vrf.objects.create(name='vrf')

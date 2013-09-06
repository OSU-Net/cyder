from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.cydhcp.vrf.models import Vrf


class VrfAPI_Test(DHCPAPITests):
    model = Vrf

    def create_data(self):
        return self.model.objects.get_or_create(name='vrf')[0]


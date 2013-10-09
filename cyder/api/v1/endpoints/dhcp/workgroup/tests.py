from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.cydhcp.workgroup.models import Workgroup


class WorkgroupAPI_Test(DHCPAPITests):
    model = Workgroup

    def create_data(self):
        return self.model.objects.get_or_create(name='workgroup')[0]

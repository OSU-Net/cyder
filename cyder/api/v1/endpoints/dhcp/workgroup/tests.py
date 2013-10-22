from cyder.cydhcp.workgroup.models import Workgroup
from cyder.api.v1.tests.base import APITests, APIEAVTestMixin


class WorkgroupAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = Workgroup

    def create_data(self):
        return self.model.objects.get_or_create(name='workgroup')[0]

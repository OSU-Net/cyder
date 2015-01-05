from cyder.api.v1.tests.base import APIEAVTestMixin, APITests
from cyder.core.system.models import System


class SystemAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = System

    def create_data(self):
        return System.objects.create(name='test_system')

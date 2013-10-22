from cyder.api.v1.tests.base import APIEAVTestMixin, APITests
from cyder.core.system.models import System


class SystemAPI_Test(APITests, APIEAVTestMixin):
    __test__ = True
    model = System

    def create_data(self):
        data = {
            'name': 'test_system',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

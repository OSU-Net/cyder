from cyder.api.v1.tests.base import APIKVTestMixin, APITests
from cyder.core.system.models import System


class SystemAPI_Test(APITests, APIKVTestMixin):
    __test__ = True
    model = System
    keyvalue_attr = "systemkeyvalue_set"

    def create_data(self):
        data = {
            'name': 'test_system',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

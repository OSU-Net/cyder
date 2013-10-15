from cyder.api.v1.tests.base import APIKVTestMixin
from cyder.cydns.soa.models import SOA
from cyder.api.v1.tests.base import APITests


class SOAAPI_Test(APITests, APIKVTestMixin):
    __test__ = True
    model = SOA
    keyvalue_attr = "keyvalue_set"

    def create_data(self):
        data = {
            'primary': 'ns1.oregonstate.edu',
            'contact': 'admin.oregonstate.edu',
            'retry': 420,
            'refresh': 420,
            'description': 'Test SOA',
        }
        obj, _ = SOA.objects.get_or_create(**data)
        return obj

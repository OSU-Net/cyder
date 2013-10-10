from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.api.v1.tests.base import APIKVTestMixin
from cyder.cydns.soa.models import SOA


class SOAAPI_Test(DNSAPITests, APIKVTestMixin):
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

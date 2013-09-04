from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.soa.models import SOA


class SOAAPI_Test(DNSAPITests):
    model = SOA

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

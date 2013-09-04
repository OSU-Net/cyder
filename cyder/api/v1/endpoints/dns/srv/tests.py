from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.srv.models import SRV


class SRVAPI_Test(DNSAPITests):
    model = SRV

    def create_data(self):
        data = {
            'description': 'SRV',
            'ttl': 420,
            'label': '_srv',
            'domain': self.domain,
            'target': 'foo.example.com',
            'priority': 420,
            'weight': 420,
            'port': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

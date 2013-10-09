from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.mx.models import MX


class MXAPI_Test(DNSAPITests):
    model = MX

    def create_data(self):
        data = {
            'description': 'MX Record',
            'label': 'mail',
            'domain': self.domain,
            'server': 'relay.oregonstate.edu',
            'ttl': 420,
            'priority': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

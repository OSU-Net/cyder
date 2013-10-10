from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.nameserver.models import Nameserver


class NameserverAPI_Test(DNSAPITests):
    model = Nameserver

    def create_data(self):
        data = {
            'server': 'relay.oregonstate.edu',
            'description': 'Nameserver Record',
            'ttl': 420,
            'domain': self.domain,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

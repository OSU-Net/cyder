from cyder.cydns.nameserver.models import Nameserver
from cyder.api.v1.tests.base import APITests


class NameserverAPI_Test(APITests):
    __test__ = True
    model = Nameserver

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
            'server': 'relay.oregonstate.edu',
            'description': 'Nameserver Record',
            'ttl': 420,
            'domain': self.domain,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

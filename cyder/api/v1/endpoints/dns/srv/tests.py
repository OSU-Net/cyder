from cyder.cydns.srv.models import SRV
from cyder.api.v1.tests.base import APITests


class SRVAPI_Test(APITests):
    __test__ = True
    model = SRV

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
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

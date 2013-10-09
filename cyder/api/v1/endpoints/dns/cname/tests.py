from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.cname.models import CNAME


class CNAMEAPI_Test(DNSAPITests):
    model = CNAME

    def create_data(self):
        data = {
            'description': 'CNAME record',
            'ttl': 420,
            'label': 'baz',
            'domain': self.domain,
            'target': 'bar.' + self.domain.name,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.views.add(self.view.id)
        return obj

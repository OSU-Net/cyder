from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.txt.models import TXT


class TXTAPI_Test(DNSAPITests):
    model = TXT

    def create_data(self):
        data = {
            'label': 'txt',
            'domain': self.domain,
            'txt_data': 'Things',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

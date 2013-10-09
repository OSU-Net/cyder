from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.sshfp.models import SSHFP


class SSHFPAPI_Test(DNSAPITests):
    model = SSHFP

    def create_data(self):
        data = {
            'description': 'SSHFP Record',
            'ttl': 420,
            'label': 'sshfp',
            'domain': self.domain,
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '0123456789abcdef0123456789abcdef01234567',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

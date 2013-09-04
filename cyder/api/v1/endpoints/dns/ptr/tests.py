from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.domain.models import Domain
from cyder.cydns.ptr.models import PTR


class PTRBase(DNSAPITests):
    model = PTR

    def create_data(self):
        Domain.objects.get_or_create(name='arpa')

        return {
            'description': 'PTR Record',
            'ttl': 420,
            'name': 'ptr',
        }


class PTRv4API_Test(PTRBase):
    model = PTR

    def create_data(self):
        super(PTRv4API_Test, self).create_data()
        Domain.objects.get_or_create(name='in-addr.arpa')
        Domain.objects.get_or_create(name='11.in-addr.arpa')

        data = {
            'ip_str': '11.1.2.3',
            'ip_type': '4',
        }

        obj, _ = self.model.objects.get_or_create(**data)
        return obj


class PTRv6API_Test(PTRBase):
    model = PTR

    def create_data(self):
        super(PTRv6API_Test, self).create_data()
        Domain.objects.get_or_create(name='ip6.arpa')
        Domain.objects.get_or_create(name='1.ip6.arpa')

        data = {
            'ip_str': '1000:2000:3000:0000:0000:4000:5000:6000',
            'ip_type': '6',
        }

        obj, _ = self.model.objects.get_or_create(**data)
        return obj

from cyder.api.v1.tests.base import APITests, create_network_range
from cyder.cydns.domain.models import Domain
from cyder.cydns.ptr.models import PTR
from cyder.cydns.tests.utils import create_zone


class PTRv4API_Test(APITests):
    __test__ = True
    model = PTR

    def create_data(self):
        Domain.objects.create(name='arpa')
        Domain.objects.create(name='in-addr.arpa')
        create_zone('11.in-addr.arpa')
        create_network_range(
            network_str='11.1.2.0/24', start_str='11.1.2.1',
            end_str='11.1.2.127', range_type='st', ip_type='4',
            domain=self.domain, ctnr=self.ctnr)

        return PTR.objects.create(
            ctnr=self.ctnr, description='PTR Record', ttl=420,
            fqdn=('ptr.' + self.domain.name), ip_str='11.1.2.3', ip_type='4')


class PTRv6API_Test(APITests):
    __test__ = True
    model = PTR

    def create_data(self):
        Domain.objects.create(name='arpa')
        Domain.objects.create(name='ip6.arpa')
        create_zone('1.ip6.arpa')
        create_network_range(
            network_str='1000:2000::/32',
            start_str='1000:2000:3000::4000:5000:5000',
            end_str='1000:2000:3000::4000:5000:6000', range_type='st',
            ip_type='6', domain=self.domain, ctnr=self.ctnr)

        return PTR.objects.create(
            ctnr=self.ctnr, description='PTR Record', ttl=420,
            fqdn=('ptr.' + self.domain.name),
            ip_str='1000:2000:3000:0000:0000:4000:5000:6000', ip_type='6')

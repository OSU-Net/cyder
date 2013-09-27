from cyder.api.v1.endpoints.dhcp.tests import DHCPAPITests
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.domain.models import Domain


class StaticInterfaceBase(DHCPAPITests):
    model = StaticInterface
    urlname = "static_interface"
    keyvalue_attr = "staticintrkeyvalue_set"

    def __init__(self, *args, **kwargs):
        Domain.objects.get_or_create(name='arpa')
        self.ctnr, _ = Ctnr.objects.get_or_create(name="TestCtnr")
        self.system, _ = System.objects.get_or_create(name="TestSystem")
        super(StaticInterfaceBase, self).__init__(self, *args, **kwargs)

    def create_data(self):
        return {
            'ctnr': self.ctnr,
            'description': 'Test Static Interface',
            'ttl': 420,
            'mac': '11:22:33:44:55:00',
            'system': self.system,
            'label': 'stat',
            'domain': self.domain,
            'dhcp_enabled': False,
            'dns_enabled': True,
        }


class StaticInterfaceV4API_Test(StaticInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(StaticInterfaceV4API_Test, self).__init__(self, *args, **kwargs)
        Domain.objects.get_or_create(name='in-addr.arpa')
        Domain.objects.get_or_create(name='11.in-addr.arpa')

    def create_data(self):
        data = super(StaticInterfaceV4API_Test, self).create_data()
        data.update({
            'ip_str': '11.12.14.255',
            'ip_type': '4',
        })
        fack = self.model.objects.filter(**data)
        if fack:
            obj, _ = fack.all()[0]
        else:
            obj, _ = self.model.objects.get_or_create(**data)
        return obj


class StaticInterfaceV6API_Test(StaticInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(StaticInterfaceV6API_Test, self).__init__(self, *args, **kwargs)
        Domain.objects.get_or_create(name='ip6.arpa')
        Domain.objects.get_or_create(name='2.ip6.arpa')

    def create_data(self):
        data = super(StaticInterfaceV6API_Test, self).create_data()
        data.update({
            'ip_str': '2001:0db8:85a3:0000:0000:8a2e:0370:7344',
            'ip_type': '6',
        })
        fack = self.model.objects.filter(**data).all()
        if fack:
            obj, _ = fack[0]
        else:
            obj, _ = self.model.objects.get_or_create(**data)
        return obj

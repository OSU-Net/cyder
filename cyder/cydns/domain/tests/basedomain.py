from django.test import TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydhcp.network.models import Network
from cyder.cydns.domain.models import Domain
from cyder.cydns.tests.utils import create_fake_zone

from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC


class BaseDomain(TestCase):
    def setUp(self):
        Domain.objects.get_or_create(name="arpa")
        Domain.objects.get_or_create(name="in-addr.arpa")
        Domain.objects.get_or_create(name="128.in-addr.arpa")
        self.ctnr, _ = Ctnr.objects.get_or_create(name="abloobloobloo")

        c = Domain(name='poo')
        c.save()
        self.ctnr.domains.add(c)

        self.assertFalse(c.purgeable)
        self.f_c = create_fake_zone('foo.poo', suffix="")
        self.assertEqual(self.f_c.name, 'foo.poo')
        self.ctnr.domains.add(self.f_c)

        self.net = Network(network_str='10.2.3.0/29')
        self.net.update_network()
        self.net.save()
        self.sr = Range(network=self.net, range_type=STATIC,
                        start_str='10.2.3.1', end_str='10.2.3.4')
        self.sr.save()

    def create_domain(self, *args, **kwargs):
        d = Domain.objects.create(*args, **kwargs)
        self.ctnr.domains.add(d)
        return d

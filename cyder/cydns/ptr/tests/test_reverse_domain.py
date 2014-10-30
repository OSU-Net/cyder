from django.core.exceptions import ValidationError
from ipaddr import IPv6Address

from cyder.base.tests import TestCase
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import reverse_domain_name_to_ip
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import make_root


class LinearReverseDomainTests(TestCase):
    def setUp(self):
        c = Ctnr.objects.create(name='foo')

        Domain.objects.create(name='arpa')
        Domain.objects.create(name='ip6.arpa')

        self.one = Domain.objects.create(name='1.ip6.arpa')
        self.two = Domain.objects.create(name='2.1.ip6.arpa')
        self.three = Domain.objects.create(name='3.2.1.ip6.arpa')
        self.four = Domain.objects.create(name='4.3.2.1.ip6.arpa')
        self.five = Domain.objects.create(name='5.4.3.2.1.ip6.arpa')
        c.domains.add(self.one, self.two, self.three, self.four, self.five)

        make_root(self.two)
        make_root(self.four)

        for ip_str, fqdn in (
                ('1200::', 'p2'),
                ('1230::', 'p3'),
                ('1234::', 'p4'),
                ('1234:5000::', 'p5')):
            setattr(self, fqdn,
                    PTR.objects.create(
                        ip_str=ip_str, ip_type='6', fqdn=fqdn, ctnr=c))

    def add_zone(self, domain):
        make_root(domain)

    def move_zone(self, old_domain, new_domain):
        Nameserver.objects.create(domain=new_domain, server='ns1.unused')
        s = old_domain.root_of_soa.get()
        s.root_domain = new_domain
        s.save()
        old_domain.nameserver_set.all().delete()

    def remove_zone(self, domain):
        domain.soa.delete()
        domain.nameserver_set.all().delete()

    def assertMembers(self, *pairs):
        for p, d in pairs:
            self.assertIn(p, d.reverse_ptr_set.all(),
                u'{} has reverse domain {}, not {}'.format(
                    repr(p), repr(p.reverse_domain), repr(d)))

    def test_add1(self):
        self.add_zone(self.one)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.two),
                (self.p4, self.four),
                (self.p5, self.four))

    def test_add3(self):
        self.add_zone(self.three)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.three),
                (self.p4, self.four),
                (self.p5, self.four))

    def test_add5(self):
        self.add_zone(self.five)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.two),
                (self.p4, self.four),
                (self.p5, self.five))

    def test_move21(self):
        self.move_zone(self.two, self.one)

        self.assertMembers(
                (self.p2, self.one),
                (self.p3, self.one),
                (self.p4, self.four),
                (self.p5, self.four))

    def test_move23_disallowed(self):
        self.assertRaises(ValidationError,
                          self.move_zone, self.two, self.three)

    def test_move25_disallowed(self):
        self.assertRaises(ValidationError,
                          self.move_zone, self.two, self.five)

    def test_move41(self):
        self.move_zone(self.four, self.one)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.two),
                (self.p4, self.two),
                (self.p5, self.two))

    def test_move43(self):
        self.move_zone(self.four, self.three)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.three),
                (self.p4, self.three),
                (self.p5, self.three))

    def test_move45(self):
        self.move_zone(self.four, self.five)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.two),
                (self.p4, self.two),
                (self.p5, self.five))

    def test_remove2_disallowed(self):
        self.assertRaises(ValidationError,
                          self.remove_zone, self.two)

    def test_remove4(self):
        self.remove_zone(self.four)

        self.assertMembers(
                (self.p2, self.two),
                (self.p3, self.two),
                (self.p4, self.two),
                (self.p5, self.two))

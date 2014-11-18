from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.mx.models import MX
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.tests.utils import create_zone, DNSTest
from cyder.cydns.txt.models import TXT


class CNAMETests(DNSTest, ModelTestMixin):
    def setUp(self):
        super(CNAMETests, self).setUp()

        self.vrf = Vrf.objects.create(name='test_vrf')

        create_zone('128.in-addr.arpa')

        self.ctnr2 = Ctnr.objects.create(name='test_ctnr2')

        self.g = create_zone('gz')
        self.c_g = create_zone('coo.gz')
        self.d = create_zone('dz')
        Domain.objects.create(name='cd')
        self.whatcd = create_zone('what.cd')

        for dom in (self.g, self.c_g, self.d, self.whatcd):
            self.ctnr.domains.add(dom)

        self.r1 = create_zone('10.in-addr.arpa')
        self.r1.save()

        self.s = System.objects.create(name='test_system')

        self.net1 = Network.objects.create(network_str='10.0.0.0/8')

        self.net2 = Network.objects.create(network_str='128.193.1.0/30')

        self.sr1 = Range.objects.create(
            network=self.net1, range_type=STATIC, start_str='10.0.0.1',
            end_str='10.0.0.3')

        self.sr2 = Range.objects.create(
            network=self.net1, range_type=STATIC, start_str='10.193.1.1',
            end_str='10.193.1.2')

        self.sr3 = Range.objects.create(
            network=self.net2, range_type=STATIC, start_str='128.193.1.1',
            end_str='128.193.1.2')

        for r in (self.sr1, self.sr2, self.sr3):
            self.ctnr.ranges.add(r)

    def create_cname(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        return CNAME.objects.create(**kwargs)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_cname(
                label='a', domain=self.g, target='foo.com'),
            self.create_cname(
                label='bbbbbbbbbbbbbbbbb', domain=self.c_g,
                target='foo.foo.com'),
            self.create_cname(
                label='c-c-c-c-c-c-c-c-c', domain=self.g, target='foo.com'),
            self.create_cname(
                label='d1d', domain=self.g, target='foo.com'),
        )

    def test1_add_glob(self):
        self.create_cname(label='*foo', domain=self.g, target='foo.com')
        self.create_cname(label='*', domain=self.c_g, target='foo.foo.com')
        self.assertRaises(
            ValidationError, self.create_cname,
            label='*.fo1', domain=self.g, target='foo.com')
        self.create_cname(
            label='*sadfasfd-asdf', domain=self.g, target='foo.com')

    def test2_add_glob(self):
        self.create_cname(label='*coo', domain=self.g, target='foo.com')
        self.create_cname(label='*', domain=self.c_g, target='foo.com')

    def test_soa_condition(self):
        self.assertRaises(
            ValidationError, self.create_cname,
            label='', domain=self.c_g, target='foo.com')

    def test_add_bad(self):
        self.assertRaises(
            ValidationError, self.create_cname,
            label='', domain=self.g, target='..foo.com')

    def test_add_mx_with_cname(self):
        def create_mx():
            return MX.objects.create(
                label='', domain=self.c_g, ctnr=self.ctnr,
                server=('cnamederp1.' + self.c_g.name), priority=2, ttl=2222)
        create_mx.name = 'MX'

        def create_cname():
            return CNAME.objects.create(
                label='cnamederp1', domain=self.c_g, ctnr=self.ctnr,
                target='foo.com')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_mx, create_cname))

    def test_address_record_exists(self):
        def create_a():
            return AddressRecord.objects.create(
                label='testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                ip_type='4', ip_str="128.193.1.1")
        create_a.name = 'AddressRecord'

        def create_cname():
            return CNAME.objects.create(
                label='testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_a, create_cname))

    def test_address_record_exists_uppercase(self):
        def create_a():
            return AddressRecord.objects.create(
                label='testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                ip_type='4', ip_str="128.193.1.1")
        create_a.name = 'AddressRecord'

        def create_cname():
            return CNAME.objects.create(
                label='Testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_a, create_cname))

    def test_srv_exists(self):
        def create_srv():
            return SRV.objects.create(
                label='_testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                target='asdf', port=2, priority=2, weight=4)
        create_srv.name = 'SRV'

        def create_cname():
            return CNAME.objects.create(
                label='_testyfoo', ctnr=self.ctnr, domain=self.whatcd,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_srv, create_cname))

    def test_txt_exists(self):
        def create_txt():
            return TXT.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                txt_data='asdf')
        create_txt.name = 'TXT'

        def create_cname():
            return CNAME.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_txt, create_cname))

    def test_mx_exists(self):
        def create_mx():
            return MX.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                server='asdf', priority=123, ttl=123)
        create_mx.name = 'MX'

        def create_cname():
            return CNAME.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_mx, create_cname))

    def test_ns_exists(self):
        bleh = Domain.objects.create(name='bleh.what.cd')
        self.ctnr.domains.add(bleh)

        def create_ns():
            return Nameserver.objects.create(domain=bleh, server='asdf')
        create_ns.name = 'Nameserver'

        def create_cname():
            return CNAME.objects.create(
                label='', ctnr=self.ctnr, domain=bleh, target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_ns, create_cname))

    def test_intr_exists(self):
        def create_static_intr():
            return StaticInterface.objects.create(
                label='testyfoo', domain=self.whatcd, ip_str='10.0.0.1',
                ip_type='4', system=self.s, ctnr=self.ctnr,
                mac="11:22:33:44:55:66")
        create_static_intr.name = 'StaticInterface'

        def create_cname():
            return CNAME.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_static_intr, create_cname))

    def test_ptr_exists(self):
        def create_ptr():
            return PTR.objects.create(
                ip_str="10.193.1.1", ip_type='4', fqdn='testyfoo.what.cd',
                ctnr=self.ctnr)
        create_ptr.name = 'PTR'

        def create_cname():
            return CNAME.objects.create(
                label='testyfoo', domain=self.whatcd, ctnr=self.ctnr,
                target='wat')
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_ptr, create_cname))

    def test_cname_point_to_itself(self):
        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label='foopy', domain=self.whatcd, ctnr=self.ctnr,
            target='foopy.what.cd')

    def test_domain_ctnr(self):
        """Test that a CNAME's domain must be in the CNAME's container"""
        gz = Domain.objects.get(name='gz')
        self.ctnr.domains.add(gz)

        CNAME.objects.create(
            label='bar1', domain=gz, target='foo1.gz', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label='bar2', domain=gz, target='foo2.gz', ctnr=self.ctnr2)

    def test_name_uniqueness(self):
        """Test that CNAMEs must share a ctnr if they have the same name"""
        cn1 = CNAME.objects.create(
            label='bar', domain=self.g, target='foo1.gz', ctnr=self.ctnr)

        cn2 = CNAME.objects.create(
            label='bar', domain=self.g, target='foo2.gz', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label='bar', domain=self.g, target='foo3.gz', ctnr=self.ctnr2)

    def bootstrap_zone_and_range(self):
        d = Domain.objects.create(name='example.gz')
        self.ctnr.domains.add(d)

        soa = SOA.objects.create(
            root_domain=d, primary='ns.example.gz',
            contact='root.mail.example.gz')

        n = Network.objects.create(
            vrf=self.vrf, ip_type='4',
            network_str='128.193.0.0/24')

        r = Range.objects.create(
            network=n, range_type=STATIC, start_str='128.193.0.2',
            end_str='128.193.0.100')

        # Cyder has a catch-22 relating to nameservers: If a nameserver's name
        # is in the same domain it serves as a nameserver for, a glue record
        # must exist before that nameserver can be created, but the nameserver
        # must exist before the glue record can be created. Thus, we have to
        # set the nameserver's name to something outside the domain it's a
        # nameserver for, add the glue record, then fix the nameserver's name.

        ns = Nameserver.objects.create(domain=d, server='cyderhack')

        glue = AddressRecord.objects.create(
            label='ns', domain=d, ip_str='128.193.0.2', ctnr=self.ctnr)

        ns.server = 'ns.example.gz'
        ns.save()

    def test_a_mx_conflict(self):
        """Test that a CNAME cannot have the same name as an AR or MX"""

        self.bootstrap_zone_and_range()

        e_g = Domain.objects.get(name='example.gz')

        def create_cname():
            return CNAME.objects.create(
                label='foo', domain=e_g, target='bar.example.gz',
                ctnr=self.ctnr)
        create_cname.name = 'CNAME'

        def create_si():
            s = System.objects.create(name='test_system')
            return StaticInterface.objects.create(
                mac='be:ef:fa:ce:11:11', label='foo', domain=e_g,
                ip_str='128.193.0.3', ip_type='4', system=s, ctnr=self.ctnr)
        create_si.name = 'StaticInterface'

        def create_mx():
            return MX.objects.create(
                label='foo', domain=e_g, server='mail.example.gz', priority=1,
                ctnr=self.ctnr)
        create_mx.name = 'MX'

        self.assertObjectsConflict((create_cname, create_si))
        self.assertObjectsConflict((create_cname, create_mx))

    def test_soa_conflict(self):
        """Test that a CNAME cannot have the same name as an SOA"""

        self.bootstrap_zone_and_range()

        f_e_g = Domain.objects.create(name='foo.example.gz')
        self.ctnr.domains.add(f_e_g)

        def create_cname():
            return CNAME.objects.create(
                label='', domain=f_e_g.reload(), target='bar.example.gz',
                ctnr=self.ctnr)
        create_cname.name = 'CNAME'

        def create_soa():
            return SOA.objects.create(
                root_domain=f_e_g.reload(), primary='ns1.example.gz',
                contact='root.mail.example.gz')
        create_soa.name = 'SOA'

        self.assertObjectsConflict((create_cname, create_soa))

    def test_target_validation(self):
        """Test that target must be a valid non-IP hostname but need not exist
        """
        valid_targets = (
            'example.com',
            'www.example.com',
            'foo.bar.example.com',
        )

        for target in valid_targets:
            cn = CNAME.objects.create(
                label='bar', domain=self.g, target=target, ctnr=self.ctnr)
            cn.delete()

        invalid_targets = (
            '10.234.30.253',
            '128.193.0.2',
        )

        for target in invalid_targets:
            self.assertRaises(
                ValidationError, CNAME.objects.create,
                label='bar', domain=self.g, target=target, ctnr=self.ctnr)

    def test_staticinterface_conflict(self):
        """Test that a CNAME can't have the same name as a StaticInterface"""
        self.bootstrap_zone_and_range()

        d = Domain.objects.get(name='example.gz')

        def create_cname():
            return CNAME.objects.create(
                label='foo', domain=d, target='www.example.gz',
                ctnr=self.ctnr)
        create_cname.name = 'CNAME'

        def create_si():
            s = System.objects.create(name='test_system')
            return StaticInterface.objects.create(
                mac='be:ef:fa:ce:11:11', label='foo', domain=d,
                ip_str='128.193.0.3', ip_type='4', system=s,
                ctnr=self.ctnr)
        create_si.name = 'StaticInterface'

        self.assertObjectsConflict((create_cname, create_si))

    def test_duplicate_cname(self):
        def x():
            self.create_cname(label='foo', domain=self.g, target='foo.com')

        x()
        self.assertRaises(ValidationError, x)

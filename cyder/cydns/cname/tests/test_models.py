from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.mx.models import MX
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.tests.utils import create_basic_dns_data, create_fake_zone
from cyder.cydns.txt.models import TXT

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vrf.models import Vrf

from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr


class CNAMETests(cyder.base.tests.TestCase):
    def create_domain(self, name, ip_type=None, delegated=False):
        if ip_type is None:
            ip_type = '4'
        if name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
            pass
        else:
            name = ip_to_domain_name(name, ip_type=ip_type)
        d = Domain(name=name, delegated=delegated)
        d.clean()
        self.assertTrue(d.is_reverse)
        return d

    def setUp(self):
        create_basic_dns_data(dhcp=True)

        d = Domain(name='128.in-addr.arpa')
        d.full_clean()
        d.save()

        self.ctnr1 = Ctnr(name='test_ctnr1')
        self.ctnr1.full_clean()
        self.ctnr1.save()
        self.ctnr2 = Ctnr(name='test_ctnr2')
        self.ctnr2.full_clean()
        self.ctnr2.save()

        self.g = create_fake_zone("gz", suffix="")
        self.c_g = create_fake_zone("coo.gz", suffix="")
        self.d = create_fake_zone("dz", suffix="")
        self.whatcd = create_fake_zone("what.cd", suffix="")

        for dom in [self.g, self.c_g, self.d, self.whatcd]:
            self.ctnr1.domains.add(dom)

        self.r1 = create_fake_zone("10.in-addr.arpa", suffix="")
        self.r1.save()

        self.s = System()
        self.s.save()

        self.net1 = Network(network_str='10.0.0.0/8')
        self.net1.update_network()
        self.net1.save()

        self.net2 = Network(network_str='128.193.1.0/30')
        self.net2.update_network()
        self.net2.save()

        self.sr1 = Range(network=self.net1, range_type=STATIC,
                         start_str='10.0.0.1', end_str='10.0.0.3')
        self.sr1.save()

        self.sr2 = Range(network=self.net1, range_type=STATIC,
                         start_str='10.193.1.1', end_str='10.193.1.2')
        self.sr2.save()

        self.sr3 = Range(network=self.net2, range_type=STATIC,
                         start_str='128.193.1.1', end_str='128.193.1.2')
        self.sr3.save()

        for r in [self.sr1, self.sr2, self.sr3]:
            self.ctnr1.ranges.add(r)

    def do_add(self, label, domain, target):
        cn = CNAME(label=label, ctnr=self.ctnr1, domain=domain, target=target)
        cn.full_clean()
        cn.save()
        cn.save()
        self.assertTrue(cn.details())

        cs = CNAME.objects.filter(
            label=label, ctnr=self.ctnr1, domain=domain, target=target)
        self.assertEqual(len(cs), 1)
        return cn

    def test_add(self):
        label = "foo"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

        label = "boo"
        domain = self.c_g
        target = "foo.foo.com"
        self.do_add(label, domain, target)

        label = "fo1"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

        label = "hooo"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

    def test1_add_glob(self):
        label = "*foo"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

        label = "*"
        domain = self.c_g
        target = "foo.foo.com"
        self.do_add(label, domain, target)

        label = "*.fo1"
        domain = self.g
        target = "foo.com"
        self.assertRaises(ValidationError, self.do_add, *(label, domain, target))

        label = "*sadfasfd-asdf"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

    def test2_add_glob(self):
        label = "*coo"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)

        label = "*"
        domain = self.c_g
        target = "foo.com"
        self.do_add(label, domain, target)

    def test_soa_condition(self):
        label = ""
        domain = self.c_g
        target = "foo.com"
        self.assertRaises(ValidationError, self.do_add, *(label, domain, target))

    def test_add_bad(self):
        label = ""
        domain = self.g
        target = "..foo.com"
        self.assertRaises(ValidationError, self.do_add, *(label, domain, target))

    def test_add_mx_with_cname(self):
        label = "cnamederp1"
        domain = self.c_g
        target = "foo.com"

        fqdn = label + '.' + domain.name
        mx_data = {'label': '', 'domain': self.c_g, 'ctnr': self.ctnr1,
                   'server': fqdn, 'priority': 2, 'ttl': 2222}

        def create_mx():
            mx = MX(**mx_data)
            mx.save()
            return mx
        create_mx.name = 'MX'

        def create_cname():
            cn = CNAME(label=label, ctnr=self.ctnr1, domain=domain,
                       target=target)
            cn.full_clean()
            cn.save()
            return cn
        create_cname.name = 'CNAME'

        self.assertObjectsConflict((create_mx, create_cname))

    def test_address_record_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec, _ = AddressRecord.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, ip_type='4',
            ip_str="128.193.1.1")

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_address_record_exists_upper_case(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec, _ = AddressRecord.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, ip_type='4',
            ip_str="128.193.1.1")

        cn = CNAME(label=label.title(), ctnr=self.ctnr1, domain=dom,
                   target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_address_record_cname_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        CNAME.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target=target
        )
        rec = AddressRecord(label=label, ctnr=self.ctnr1, domain=dom,
                            ip_str="128.193.1.1")

        self.assertRaises(ValidationError, rec.save)

    def test_srv_exists(self):
        label = "_testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec, _ = SRV.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target="asdf",
            port=2, priority=2, weight=4)

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_srv_cname_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        CNAME.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target=target)

        rec = SRV(label=label, ctnr=self.ctnr1, domain=dom, target="asdf",
                  port=2, priority=2, weight=4)

        self.assertRaises(ValidationError, rec.save)

    def test_txt_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec, _ = TXT.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, txt_data="asdf")

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_txt_cname_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        cn, _ = CNAME.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target=target)
        cn.full_clean()
        cn.save()

        rec = TXT(label=label, ctnr=self.ctnr1, domain=dom, txt_data="asdf1")

        self.assertRaises(ValidationError, rec.save)

    def test_mx_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec, _ = MX.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, server="asdf",
            priority=123, ttl=123)

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_mx_cname_exists(self):
        # Duplicate test?
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        cn, _ = CNAME.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target=target)
        cn.full_clean()
        cn.save()

        rec = MX(label=label, ctnr=self.ctnr1, domain=dom, server="asdf1",
                 priority=123, ttl=123)

        self.assertRaises(ValidationError, rec.save)

    def test_ns_exists(self):
        # Duplicate test?
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec = Nameserver(domain=dom, server="asdf1")
        rec.save()
        cn = CNAME(label='', ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.clean)

    def test_ns_cname_exists(self):
        # Duplicate test?
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="not.cd")

        self.ctnr1.domains.add(dom)

        cn, _ = CNAME.objects.get_or_create(
            label='', ctnr=self.ctnr1, domain=dom, target=target)
        cn.full_clean()
        cn.save()

        rec = Nameserver(domain=dom, server="asdf1")
        self.assertRaises(ValidationError, rec.save)

    def test_intr_exists(self):
        label = "tdfestyfoo"
        target = "waasdft"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        intr = StaticInterface(label=label, domain=dom, ip_str="10.0.0.1",
                               ip_type='4', system=self.s, ctnr=self.ctnr1,
                               mac="11:22:33:44:55:66")
        intr.clean()
        intr.save()

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_intr_cname_exists(self):
        # Duplicate test?
        label = "tesafstyfoo"
        target = "wadfakt"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        cn, _ = CNAME.objects.get_or_create(
            label=label, ctnr=self.ctnr1, domain=dom, target=target)
        cn.full_clean()
        cn.save()

        intr = StaticInterface(
            label=label, domain=dom, ip_str="10.0.0.2", ip_type='4',
            system=self.s, mac="00:11:22:33:44:55", ctnr=self.ctnr1,
        )

        self.assertRaises(ValidationError, intr.clean)
        cn.label = "differentlabel"
        cn.save()
        intr.clean()
        intr.save()

    def test_ptr_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        rec = PTR(ctnr=self.ctnr1, ip_str="10.193.1.1", ip_type='4',
                  fqdn='testyfoo.what.cd')
        rec.clean()
        rec.full_clean()
        rec.save()

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.full_clean)

    def test_ptr_cname_exists(self):
        label = "testyfoo"
        target = "wat"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        CNAME.objects.get_or_create(label=label, ctnr=self.ctnr1, domain=dom,
                                    target=target)
        rec = PTR(ip_str="10.193.1.1", ip_type='4', fqdn='testyfoo.what.cd',
                  ctnr=self.ctnr1)

        self.assertRaises(ValidationError, rec.clean)

    def test_cname_point_to_itself(self):
        label = "foopy"
        target = "foopy.what.cd"
        dom, _ = Domain.objects.get_or_create(name="cd")
        dom, _ = Domain.objects.get_or_create(name="what.cd")

        cn = CNAME(label=label, ctnr=self.ctnr1, domain=dom, target=target)
        self.assertRaises(ValidationError, cn.clean)

    def test_domain_ctnr(self):
        """Test that a CNAME's domain must be in the CNAME's container"""
        gz = Domain.objects.get(name='gz')

        self.ctnr1.domains.add(gz)

        cn1 = CNAME(label='bar1', domain=gz, target='foo1.gz', ctnr=self.ctnr1)
        cn1.full_clean()
        cn1.save()

        with self.assertRaises(ValidationError):
            cn2 = CNAME(label='bar2', domain=gz, target='foo2.gz',
                        ctnr=self.ctnr2)
            cn2.full_clean()
            cn2.save()

    def test_name_uniqueness(self):
        """Test that CNAMEs must share a ctnr if they have the same name"""
        cn1 = CNAME(label='bar', domain=self.g, target='foo1.gz',
                    ctnr=self.ctnr1)
        cn1.full_clean()
        cn1.save()

        cn2 = CNAME(label='bar', domain=self.g, target='foo2.gz',
                    ctnr=self.ctnr1)
        cn2.full_clean()
        cn2.save()

        with self.assertRaises(ValidationError):
            cn3 = CNAME(label='bar', domain=self.g, target='foo3.gz',
                        ctnr=self.ctnr2)
            cn3.full_clean()
            cn3.save()

    def bootstrap_zone_and_range(self):
        d = Domain(name='example.gz')
        d.full_clean()
        d.save()

        self.ctnr1.domains.add(d)

        soa = SOA(root_domain=d, primary='ns.example.gz',
                  contact='root.mail.example.gz')
        soa.full_clean()
        soa.save()

        n = Network(vrf=Vrf.objects.get(name='test_vrf'), ip_type='4',
                    network_str='128.193.0.0/24')
        n.full_clean()
        n.save()

        r = Range(network=n, range_type=STATIC, start_str='128.193.0.2',
                  end_str='128.193.0.100')
        r.full_clean()
        r.save()

        # Cyder has a catch-22 relating to nameservers: If a nameserver's name
        # is in the same domain it serves as a nameserver for, a glue record
        # must exist before that nameserver can be created, but the nameserver
        # must exist before the glue record can be created. Thus, we have to
        # set the nameserver's name to something outside the domain it's a
        # nameserver for, add the glue record, then fix the nameserver's name.

        ns = Nameserver(domain=d, server='cyderhack')
        ns.full_clean()
        ns.save()

        glue = AddressRecord(label='ns', domain=d,
                             ip_str='128.193.0.2', ctnr=self.ctnr1)
        glue.full_clean()
        glue.save()

        ns.server = 'ns.example.gz'
        ns.full_clean()
        ns.save()

    def test_a_mx_soa_conflict(self):
        """Test that a CNAME cannot have the same name as an AR, MX, or SOA"""
        self.bootstrap_zone_and_range()

        d = Domain.objects.get(name='example.gz')

        def create_cname():
            cn = CNAME(label='foo', domain=d, target='bar.example.gz',
                       ctnr=self.ctnr1)
            cn.full_clean()
            cn.save()
            return cn
        create_cname.name = 'CNAME'

        def create_si():
            s = System(name='test_system')
            s.full_clean()
            s.save()

            si = StaticInterface(
                mac='be:ef:fa:ce:11:11', label='foo', domain=d,
                ip_str='128.193.0.3', ip_type='4', system=s,
                ctnr=self.ctnr1)
            si.full_clean()
            si.save()
            return si
        create_si.name = 'StaticInterface'

        def create_mx():
            mx = MX(label='foo', domain=d, server='mail.example.gz',
                    priority=1, ctnr=self.ctnr1)
            mx.full_clean()
            mx.save()
            return mx
        create_mx.name = 'MX'

        def create_soa():
            d = Domain(name='foo.example.gz')
            d.full_clean()
            d.save()

            soa = SOA(
                root_domain=d, primary='ns1.example.gz',
                contact='root.mail.example.gz',
                description='SOA for foo.example.gz'
            )
            soa.full_clean()
            soa.save()

            return d
        create_soa.name = 'SOA'

        self.assertObjectsConflict((create_cname, create_si))
        self.assertObjectsConflict((create_cname, create_mx))
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
            cn = CNAME(label='bar', domain=self.g, target=target,
                       ctnr=self.ctnr1)
            cn.full_clean()
            cn.save()
            cn.delete()

        invalid_targets = (
            '10.234.30.253',
            '128.193.0.2',
        )

        for target in invalid_targets:
            with self.assertRaises(ValidationError):
                cn = CNAME(label='bar', domain=self.g, target=target,
                           ctnr=self.ctnr1)
                cn.full_clean()
                cn.save()

    def test_staticinterface_conflict(self):
        """Test that a CNAME can't have the same name as a StaticInterface"""
        self.bootstrap_zone_and_range()

        d = Domain.objects.get(name='example.gz')

        def create_cname():
            cn = CNAME(label='foo', domain=d, target='www.example.gz',
                       ctnr=self.ctnr1)
            cn.full_clean()
            cn.save()
            return cn
        create_cname.name = 'CNAME'

        def create_si():
            s = System(name='test_system')
            s.full_clean()
            s.save()

            si = StaticInterface(
                mac='be:ef:fa:ce:11:11', label='foo', domain=d,
                ip_str='128.193.0.3', ip_type='4', system=s,
                ctnr=self.ctnr1)
            si.full_clean()
            si.save()
            return si
        create_si.name = 'StaticInterface'

        self.assertObjectsConflict((create_cname, create_si))

    def test_duplicate_cname(self):
        label = "foo"
        domain = self.g
        target = "foo.com"
        self.do_add(label, domain, target)
        self.assertRaises(ValidationError, self.do_add, label, domain, target)

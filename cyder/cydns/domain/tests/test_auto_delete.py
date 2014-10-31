from cyder.core.system.models import System
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.cname.models import CNAME
from cyder.cydns.txt.models import TXT
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.utils import ensure_label_domain, prune_tree
from cyder.cydns.tests.utils import create_zone

from basedomain import BaseDomain


class AutoDeleteTests(BaseDomain):
    def test_cleanup_txt(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        self.assertFalse(self.f_c.purgeable)
        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)

        txt = TXT.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, txt_data="Nothing")
        self.assertFalse(prune_tree(the_domain))
        txt.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

    def test_cleanup_address(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        addr = AddressRecord.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, ip_type='4',
            ip_str="10.2.3.4")
        self.assertFalse(prune_tree(the_domain))
        addr.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo"))
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

    def test_cleanup_mx(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        mx = MX.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, server="foo",
            priority=4)
        self.assertFalse(prune_tree(the_domain))
        mx.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

    def test_ns_cleanup(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        ns = Nameserver.objects.create(
            ctnr=self.ctnr, domain=the_domain, server="asdfasffoo")
        self.assertFalse(prune_tree(the_domain))
        ns.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

    def test_srv_cleanup(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        srv = SRV.objects.create(
            label='_' + label, ctnr=self.ctnr, domain=the_domain, target="foo",
            priority=4, weight=4, port=34)
        self.assertFalse(prune_tree(the_domain))
        srv.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

    def test_cleanup_cname(self):
        # Make sure CNAME record block
        c = Domain.objects.create(name='foo1')
        self.assertFalse(c.purgeable)
        f_c = create_zone('foo.foo1')
        self.ctnr.domains.add(f_c)
        self.assertEqual(f_c.name, 'foo.foo1')

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.foo1").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.foo1").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.foo1").exists())
        self.assertTrue(Domain.objects.filter(name="foo.foo1").exists())

        self.assertFalse(f_c.purgeable)
        fqdn = "cname.x.y.z.foo.foo1"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)

        cname = CNAME.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, target="foo")
        self.assertFalse(prune_tree(the_domain))
        cname.delete()

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.foo1").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.foo1").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.foo1").exists())
        fqdn = "bar.x.y.z.foo.poo"
        self.assertTrue(Domain.objects.filter(name="foo.foo1").exists())

    def test_cleanup_intr(self):
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

        create_zone('10.in-addr.arpa')

        fqdn = "bar.x.y.z.foo.poo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        system = System.objects.create(name='foobar')
        addr = StaticInterface.objects.create(
            label=label, domain=the_domain, ip_type='4', ip_str="10.2.3.4",
            mac="00:11:22:33:44:55", system=system, ctnr=self.ctnr,)
        self.assertFalse(prune_tree(the_domain))
        addr.delete(**{'delete_system': False})

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="y.z.foo.poo").exists())
        self.assertFalse(Domain.objects.filter(name="z.foo.poo").exists())
        self.assertTrue(Domain.objects.filter(name="foo.poo").exists())

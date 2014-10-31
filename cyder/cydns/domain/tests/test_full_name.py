from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.txt.models import TXT
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import create_zone
from cyder.cydns.utils import ensure_domain, ensure_label_domain, prune_tree

from basedomain import BaseDomain


class FullNameTests(BaseDomain):
    def test_basic_add_remove1(self):
        c = Domain.objects.create(name='com')
        self.assertFalse(c.purgeable)

        f_c = Domain.objects.create(name='foo.com')
        s = SOA.objects.create(
            primary="foo", contact="foo", root_domain=f_c,
            description="foo.zfoo.comom")
        f_c = f_c.reload()
        self.assertFalse(f_c.purgeable)

        fqdn = "bar.x.y.z.foo.com"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        self.assertEqual(label, "bar")
        self.assertEqual(the_domain.name, "x.y.z.foo.com")
        self.assertTrue(the_domain.purgeable)
        self.assertEqual(the_domain.master_domain.name, "y.z.foo.com")
        self.assertTrue(the_domain.master_domain.purgeable)
        self.assertEqual(
            the_domain.master_domain.master_domain.name, "z.foo.com")
        self.assertTrue(the_domain.master_domain.master_domain.purgeable)
        self.assertEqual(
            the_domain.master_domain.master_domain.master_domain.name,
            "foo.com"
        )
        self.assertFalse(
            the_domain.master_domain.master_domain.master_domain.purgeable)

        # Now call prune_tree on the_domain.
        self.assertTrue(prune_tree(the_domain))

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.com"))
        self.assertFalse(Domain.objects.filter(name="y.z.foo.com"))
        self.assertFalse(Domain.objects.filter(name="z.foo.com"))
        self.assertTrue(Domain.objects.filter(name="foo.com"))

        # Make sure other domain's can't be pruned.
        self.assertFalse(prune_tree(f_c))
        self.assertTrue(Domain.objects.filter(name="foo.com"))
        self.assertFalse(prune_tree(c))
        self.assertTrue(Domain.objects.filter(name="com"))

    def test_basic_add_remove2(self):
        # Make sure that if a domain is set to not purgeable the prune stops at
        # that domain.
        c = Domain.objects.create(name='edu')
        self.assertFalse(c.purgeable)
        f_c = Domain.objects.create(name='foo.edu')
        s = SOA.objects.create(
            primary="foo", contact="foo", root_domain=f_c,
            description="foo.edu")
        f_c = f_c.reload()

        self.assertFalse(f_c.purgeable)
        fqdn = "bar.x.y.z.foo.edu"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        self.assertEqual(label, "bar")
        self.assertEqual(the_domain.name, "x.y.z.foo.edu")
        self.assertTrue(the_domain.purgeable)
        self.assertEqual(the_domain.master_domain.name, "y.z.foo.edu")
        self.assertTrue(the_domain.master_domain.purgeable)
        self.assertEqual(
            the_domain.master_domain.master_domain.name, "z.foo.edu")
        self.assertTrue(the_domain.master_domain.master_domain.purgeable)
        self.assertEqual(
            the_domain.master_domain.master_domain.master_domain.name,
            "foo.edu"
        )
        self.assertFalse(
            the_domain.master_domain.master_domain.master_domain.purgeable)

        # See if purgeable stops prune.
        the_domain.purgeable = False
        the_domain.save()
        self.assertFalse(prune_tree(the_domain))
        the_domain.purgeable = True
        the_domain.save()
        # OK, reset.

        y_z = Domain.objects.get(name="y.z.foo.edu")
        y_z.purgeable = False
        y_z.save()

        # Reload the domain.
        the_domain = the_domain.reload()
        # This should delete up to and stop at the domain "y.z.foo.edu".
        self.assertTrue(prune_tree(the_domain))

        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.edu"))
        self.assertTrue(Domain.objects.filter(name="y.z.foo.edu"))
        self.assertTrue(Domain.objects.filter(name="z.foo.edu"))
        self.assertTrue(Domain.objects.filter(name="foo.edu"))

        # If we delete y.z.foo.com and then call prune on z.foo.com is should
        # delete z.foo.com.
        Domain.objects.get(name="y.z.foo.edu").delete()

        self.assertTrue(prune_tree(Domain.objects.get(name="z.foo.edu")))
        self.assertFalse(Domain.objects.filter(name="z.foo.edu"))
        self.assertTrue(Domain.objects.filter(name="foo.edu"))

    def test_basic_add_remove3(self):
        # Make sure that if a domain is set to not purgeable the prune stops at
        # that domain when a record exists in a domain.
        Domain.objects.create(name='foo')
        f_c = create_zone('foo.foo')
        self.assertFalse(f_c.purgeable)

        fqdn = "bar.x.y.z.foo.foo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)

        txt = TXT.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, txt_data="Nothing")

        self.assertTrue(the_domain.purgeable)
        # txt makes the domain un-purgeable.
        self.assertFalse(prune_tree(the_domain))
        txt.delete()
        # The tree should have pruned itself.

        # Make sure stuff was deleted.
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.foo"))
        self.assertFalse(Domain.objects.filter(name="y.z.foo.foo"))
        self.assertFalse(Domain.objects.filter(name="z.foo.foo"))
        self.assertTrue(Domain.objects.filter(name="foo.foo"))

    def test_basic_add_remove4(self):
        # Move a record down the tree testing prune's ability to not delete
        # stuff.
        Domain.objects.create(name='goo')
        f_c = create_zone('foo.goo')
        self.assertFalse(f_c.purgeable)

        fqdn = "bar.x.y.z.foo.goo"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        txt = TXT.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, txt_data="Nothing")

        self.assertTrue(the_domain.purgeable)

        # txt makes the domain un-purgeable.
        self.assertFalse(prune_tree(the_domain))
        the_next_domain = the_domain.master_domain
        txt.domain = the_next_domain
        self.ctnr.domains.add(the_next_domain)
        txt.save()
        self.assertFalse(Domain.objects.filter(pk=the_domain.pk).exists())
        # We should be able to delete now.
        self.assertTrue(prune_tree(the_domain))
        the_domain = the_next_domain

        # txt makes the domain un-purgeable. y.z.foo.com
        self.assertFalse(prune_tree(the_domain))
        the_next_domain = the_domain.master_domain
        txt.domain = the_next_domain
        self.ctnr.domains.add(the_next_domain)
        txt.save()
        self.assertFalse(Domain.objects.filter(pk=the_domain.pk))
        # We should be able to delete now.
        the_domain = the_next_domain

        # txt makes the domain un-purgeable. z.foo.com
        self.assertFalse(prune_tree(the_domain))
        the_next_domain = the_domain.master_domain
        txt.domain = the_next_domain
        self.ctnr.domains.add(the_next_domain)
        txt.save()
        self.assertFalse(Domain.objects.filter(pk=the_domain.pk).exists())
        # We should be able to delete now.
        the_domain = the_next_domain

        # txt makes the domain un-purgeable. foo.com
        self.assertFalse(prune_tree(the_domain))

    def test_basic_add_remove5(self):
        # Make sure all record types block
        Domain.objects.create(name='foo22')
        f_c = create_zone('foo.foo22')
        self.assertFalse(f_c.purgeable)

        fqdn = "bar.x.y.z.foo.foo22"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)

        txt = TXT.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, txt_data="Nothing")
        self.assertFalse(prune_tree(the_domain))
        txt.delete()

        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        addr = AddressRecord.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, ip_type='4',
            ip_str="10.2.3.4")
        self.assertFalse(prune_tree(the_domain))
        addr.delete()

        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        mx = MX.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, server="foo",
            priority=4)
        self.assertFalse(prune_tree(the_domain))
        mx.delete()

        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        ns = Nameserver.objects.create(
            ctnr=self.ctnr, domain=the_domain, server="asdfasffoo")
        self.assertFalse(prune_tree(the_domain))
        ns.delete()

        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        srv = SRV.objects.create(
            label='_' + label, ctnr=self.ctnr, domain=the_domain, target="foo",
            priority=4, weight=4, port=34)
        self.assertFalse(prune_tree(the_domain))
        srv.delete()

    def test_basic_add_remove6(self):
        # Make sure CNAME record block
        Domain.objects.create(name='foo1')
        f_c = create_zone('foo.foo1')
        f_c.save()
        self.assertFalse(f_c.purgeable)

        fqdn = "cname.x.y.z.foo.foo1"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)

        cname = CNAME.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, target="foo")
        self.assertFalse(prune_tree(the_domain))
        cname.delete()

    def test_basic_add_remove7(self):
        # try a star record
        Domain.objects.create(name='foo2')
        f_c = create_zone('foo.foo2')
        f_c.save()
        self.assertFalse(f_c.purgeable)
        fqdn = "*.x.y.z.foo.foo2"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        self.assertEqual('*', label)

        cname = CNAME.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, target="foo")
        self.assertFalse(prune_tree(the_domain))
        cname.delete()

    def test_basic_add_remove8(self):
        # Make sure a record's label is changed to '' when a domain with the
        # same name as it's fqdn is created.
        Domain.objects.create(name='foo3')
        f_c = create_zone('foo.foo3')
        self.assertFalse(f_c.purgeable)

        fqdn = "www.x.y.z.foo.foo3"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        self.assertEqual('www', label)
        self.assertEqual('x.y.z.foo.foo3', the_domain.name)
        self.assertTrue(the_domain.pk)

        cname = CNAME.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, target="foo")
        fqdn = "*.www.x.y.z.foo.foo3"
        the_domain.save()
        label2, the_domain2 = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain2)
        cname = CNAME.objects.get(fqdn=cname.fqdn)
        self.assertEqual('', cname.label)
        self.assertEqual('www.x.y.z.foo.foo3', cname.domain.name)
        self.assertEqual('*', label2)
        self.assertEqual('www.x.y.z.foo.foo3', the_domain2.name)

    def test_basic_add_remove9(self):
        # Make sure all record types block.
        Domain.objects.create(name='foo22')
        f_c = create_zone('foo.foo22')
        self.assertFalse(f_c.purgeable)

        fqdn = "y.z.foo.foo22"
        label, the_domain = ensure_label_domain(fqdn)
        self.ctnr.domains.add(the_domain)
        addr = AddressRecord.objects.create(
            label=label, ctnr=self.ctnr, domain=the_domain, ip_type='4',
            ip_str="10.2.3.4")
        self.assertFalse(prune_tree(the_domain))

        new_domain = ensure_domain('y.z.foo.foo22')
        self.assertFalse(new_domain.purgeable)

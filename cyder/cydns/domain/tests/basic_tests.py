from django.core.exceptions import ValidationError

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import make_root

from basedomain import BaseDomain


class DomainTests(BaseDomain):
    def test_remove_domain(self):
        c = Domain(name='com')
        c.save()
        f_c = Domain(name='foo.com')
        f_c.save()
        f_c.delete()
        foo = Domain(name='foo.com')
        str(foo)
        foo.__repr__()

    def test1_add_domain(self):
        c = Domain(name='com')
        c.save()

        f_c = Domain(name='foo.com')
        f_c.save()
        f_c.save()
        f_c.details()
        self.assertTrue(f_c.master_domain == c)

        b_c = Domain(name='bar.com')
        b_c.save()
        self.assertTrue(b_c.master_domain == c)

        b_b_c = Domain(name='baz.bar.com')
        b_b_c.save()
        self.assertTrue(b_b_c.master_domain == b_c)

    def test2_add_domain(self):
        # Some domains have '_' in their name. Make sure validation allows
        # this.
        c = Domain(name='cz')
        c.save()
        c1 = Domain(name='_foo.cz')
        c1.save()
        c2 = Domain(name='moo_foo._foo.cz')
        c2.save()

    def test_soa_validators(self):
        m = Domain(name='moo')
        m.save()

        f_m = Domain(name='foo.moo')
        f_m.save()

        n_f_m = Domain(name='noo.foo.moo')
        n_f_m.save()

        b_m = Domain(name='baz.moo')
        b_m.save()

        s = SOA(primary="ns1.foo.com", contact="asdf", description="test",
                root_domain=f_m)
        s.save()

        n_f_m = Domain.objects.get(pk=n_f_m.pk)  # Refresh object
        self.assertEqual(n_f_m.soa, s)

        s.root_domain = m
        s.save()

        b_m = Domain.objects.get(pk=b_m.pk)  # Refresh object
        self.assertEqual(b_m.soa, s)

        s2 = SOA(primary="ns2.foo.com", contact="asdf",
                 description="test2", root_domain=m)
        self.assertRaises(ValidationError, s2.save)

    def test_2_soa_validators(self):
        d, _ = Domain.objects.get_or_create(name="gaz")
        s1, _ = SOA.objects.get_or_create(
            primary="ns1.foo.gaz", contact="hostmaster.foo",
            description="foo.gaz2", root_domain=d)
        d1, _ = Domain.objects.get_or_create(name="foo.gaz")
        s1.root_domain = d1
        s1.save()

    def test_3_soa_validators(self):
        r, _ = Domain.objects.get_or_create(name='9.in-addr.arpa')
        r.save()
        s1, _ = SOA.objects.get_or_create(
            primary="ns1.foo2.gaz", contact="hostmaster.foo",
            description="foo.gaz2", root_domain=r)

        d, _ = Domain.objects.get_or_create(name="gaz")

    def test__name_to_master_domain(self):
        try:
            Domain(name='foo.cn').save()
        except ValidationError, e:
            pass
        self.assertEqual(ValidationError, type(e))
        str(e)
        e = None

        Domain(name='cn').save()
        d = Domain(name='foo.cn')
        d.save()
        d = Domain(name='foo.cn')
        self.assertRaises(ValidationError, d.save)

    def test_create_domain(self):
        try:
            Domain(name='foo.bar.oregonstate.edu').save()
        except ValidationError, e:
            pass
        self.assertEqual(ValidationError, type(e))
        e = None

    def test_remove_has_child_domain(self):
        Domain(name='com').save()
        f_c = Domain(name='foo.com')
        f_c.save()
        Domain(name='boo.foo.com').save()
        self.assertRaises(ValidationError, f_c.delete)

    def test_invalid_add(self):

        bad = "asfda.as df"
        dom = Domain(name=bad)
        self.assertRaises(ValidationError, dom.save)

        bad = "."
        dom = Domain(name=bad)
        self.assertRaises(ValidationError, dom.save)

        bad = "edu. "
        dom = Domain(name=bad)
        self.assertRaises(ValidationError, dom.save)

        bad = ""
        dom = Domain(name=bad)
        self.assertRaises(ValidationError, dom.save)

        bad = "!@#$"
        dom = Domain(name=bad)
        self.assertRaises(ValidationError, dom.save)

    def test_remove_has_child_records(self):
        pass
        # Make sure deleting a domain doesn't leave stuff hanging.
        # TODO A records, Mx, TXT... all of the records!!

    def test_delegation_add_domain(self):
        boom = self.create_domain(name='boom')
        boom = make_root(boom)
        bleh = self.create_domain(name='bleh.boom', delegated=True)

        baa = Domain(name='baa.bleh.boom', delegated=False)
        self.assertRaises(ValidationError, baa.save)

    def test_delegation(self):
        boom = self.create_domain(name='boom')
        boom = make_root(boom)

        bleh = self.create_domain(name='bleh.boom', delegated=True)

        # Creating objects in the domain should be disallowed.
        arec = AddressRecord(
            label="ns1", ctnr=self.ctnr, domain=bleh, ip_str="128.193.99.9",
            ip_type='4')
        self.assertRaises(ValidationError, arec.save)

        ns = Nameserver(ctnr=self.ctnr, domain=bleh, server="ns1." + bleh.name)
        self.assertRaises(ValidationError, ns.save)

        cn = CNAME(label="999asdf", ctnr=self.ctnr, domain=bleh,
                   target="asdf.asdf")
        self.assertRaises(ValidationError, cn.save)

        # Undelegate the domain.
        bleh.delegated = False
        bleh.save()

        # Add glue and NS record.
        arec.save()
        ns.save()

        # Re-delegate the domain.
        bleh.delegated = True
        bleh.save()

        # Creation should still be disallowed.
        arec1 = AddressRecord(
            label="ns2", ctnr=self.ctnr, domain=bleh, ip_str="128.193.99.9",
            ip_type='4')
        self.assertRaises(ValidationError, arec1.save)

        cn1 = CNAME(label="1000asdf", ctnr=self.ctnr, domain=bleh,
                target="asdf.asdf")
        self.assertRaises(ValidationError, cn1.save)

        # Editing should be allowed.
        arec = AddressRecord.objects.get(pk=arec.pk)
        arec.ip_str = "129.193.88.2"
        arec.save()

        # Adding new A records that have the same name as an NS should
        # be allowed.
        arec1 = AddressRecord(
            label="ns1", ctnr=self.ctnr, domain=bleh, ip_str="128.193.100.10",
            ip_type='4')
        arec1.save()

    def test_existing_record_new_domain(self):
        name = "bo"
        b_dom = self.create_domain(name=name, delegated=False)

        name = "to.bo"
        t_dom = self.create_domain(name=name, delegated=False)

        arec1 = AddressRecord(
            label="no", ctnr=self.ctnr, domain=t_dom, ip_str="128.193.99.9", ip_type='4')
        arec1.save()

        name = "no.to.bo"
        n_dom = Domain(name=name, delegated=False)
        self.assertRaises(ValidationError, n_dom.save)

    def test_existing_cname_new_domain(self):
        name = "bo"
        b_dom = self.create_domain(name=name, delegated=False)

        name = "to.bo"
        t_dom = self.create_domain(name=name, delegated=False)

        cn = CNAME(ctnr=self.ctnr, domain=t_dom, label="no", target="asdf")
        cn.save()

        name = "no.to.bo"
        n_dom = Domain(name=name, delegated=False)
        self.assertRaises(ValidationError, n_dom.save)

    def test_rename_has_child_domain(self):
        name = "sucks"
        a_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        a_dom.save()

        name = "teebow.sucks"
        b_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        b_dom.save()

        name = "adsfme"
        c_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        c_dom.save()

        self.assertTrue(b_dom.master_domain == a_dom)

        try:
            c_dom.name = "asdfme"
            c_dom.save()
        except:
            self.fail("Should be able to rename domain")

        a_dom.name = "sucks2"
        self.assertRaises(ValidationError, a_dom.save)

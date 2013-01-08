from django.core.exceptions import ValidationError
from django.test import TestCase

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA


class DomainTests(TestCase):

    def setUp(self):
        Domain.objects.get_or_create(name="arpa")
        Domain.objects.get_or_create(name="in-addr.arpa")
        Domain.objects.get_or_create(name="128.in-addr.arpa")

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

        s = SOA(primary="ns1.foo.com", contact="asdf", description="test")
        s.save()

        f_m.soa = s
        f_m.save()

        b_m.soa = s
        self.assertRaises(ValidationError, b_m.save)

        n_f_m = Domain.objects.get(pk=n_f_m.pk)  # Refresh object
        n_f_m.soa = s
        n_f_m.save()

        m.soa = s
        m.save()

        b_m.soa = s
        b_m.save()

        m.soa = None
        self.assertRaises(ValidationError, m.save)

        s2 = SOA(primary="ns1.foo.com", contact="asdf", description="test2")
        s2.save()

        m.soa = s2
        self.assertRaises(ValidationError, m.save)

    def test_2_soa_validators(self):
        s1, _ = SOA.objects.get_or_create(primary="ns1.foo.gaz",
                            contact="hostmaster.foo", description="foo.gaz2")
        d, _ = Domain.objects.get_or_create(name="gaz")
        d.soa = None
        d.save()
        d1, _ = Domain.objects.get_or_create(name="foo.gaz")
        d1.soa = s1
        d1.save()

    def test_3_soa_validators(self):
        s1, _ = SOA.objects.get_or_create(primary="ns1.foo2.gaz",
                            contact="hostmaster.foo", description="foo.gaz2")

        r, _ = Domain.objects.get_or_create(name='9.in-addr.arpa')
        r.soa = s1
        r.save()

        d, _ = Domain.objects.get_or_create(name="gaz")
        d.soa = s1
        self.assertRaises(ValidationError, d.save)

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
        name = "boom1"
        dom = Domain(name=name, delegated=True)
        dom.save()

        name = "boom.boom1"
        dom = Domain(name=name, delegated=False)
        self.assertRaises(ValidationError, dom.save)

    def test_delegation(self):
        name = "boom"
        dom = Domain(name=name, delegated=True)
        dom.save()

        # Creating objects in the domain should be locked.
        arec = AddressRecord(
            label="ns1", domain=dom, ip_str="128.193.99.9", ip_type='4')
        self.assertRaises(ValidationError, arec.save)

        ns = Nameserver(domain=dom, server="ns1." + dom.name)
        self.assertRaises(ValidationError, ns.save)

        cn = CNAME(label="999asdf", domain=dom, target="asdf.asdf")
        self.assertRaises(ValidationError, cn.full_clean)

        # Undelegate (unlock) the domain.
        dom.delegated = False
        dom.save()

        # Add glue and ns record.
        arec.save()
        ns.save()

        # Re delegate the domain.
        dom.delegated = True
        dom.save()

        # Creation should still be locked
        arec1 = AddressRecord(
            label="ns2", domain=dom, ip_str="128.193.99.9", ip_type='4')
        self.assertRaises(ValidationError, arec1.save)

        cn1 = CNAME(label="1000asdf", domain=dom, target="asdf.asdf")
        self.assertRaises(ValidationError, cn1.full_clean)

        # Editing should be allowed.
        arec = AddressRecord.objects.get(pk=arec.pk)
        arec.ip_str = "129.193.88.2"
        arec.save()

        # Adding new A records that have the same name as an NS should
        # be allows.
        arec1 = AddressRecord(
            label="ns1", domain=dom, ip_str="128.193.100.10", ip_type='4')
        arec1.save()

    def test_existing_record_new_domain(self):
        name = "bo"
        b_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)

        name = "to.bo"
        t_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)

        arec1 = AddressRecord(
            label="no", domain=t_dom, ip_str="128.193.99.9", ip_type='4')
        arec1.save()

        name = "no.to.bo"
        n_dom = Domain(name=name, delegated=False)
        self.assertRaises(ValidationError, n_dom.save)

    def test_existing_cname_new_domain(self):
        name = "bo"
        b_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)

        name = "to.bo"
        t_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)

        cn = CNAME(domain=t_dom, label="no", target="asdf")
        cn.full_clean()
        cn.save()

        name = "no.to.bo"
        n_dom = Domain(name=name, delegated=False)
        self.assertRaises(ValidationError, n_dom.save)

    def test_remove_domain_with_child_objects(self):
        """Removing a domain should remove CNAMES and PTR records that
        have data in that domain."""

        name = "sucks"
        a_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        a_dom.save()

        name = "teebow.sucks"
        b_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        b_dom.save()

        name = "adsfme"
        c_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        c_dom.save()

        cn, _ = CNAME.objects.get_or_create(domain=c_dom, label="nddo",
                                            target="really.teebow.sucks")
        cn.full_clean()
        cn.save()

        ptr = PTR(
            ip_str="128.193.2.1", name="seriously.teebow.sucks", ip_type='4')
        ptr.full_clean()
        ptr.save()

        self.assertTrue(cn.target_domain == b_dom)
        self.assertTrue(ptr.data_domain == b_dom)

        b_dom, _ = Domain.objects.get_or_create(
            name="teebow.sucks", delegated=False)
        b_dom.delete()

        try:
            cn = CNAME.objects.get(pk=cn.pk)
        except:
            self.fail("CNAME was deleted.")
        self.assertTrue(cn.target_domain == a_dom)

        try:
            ptr = PTR.objects.get(pk=ptr.pk)
        except:
            self.fail("PTR was deleted")
        self.assertTrue(ptr.data_domain == a_dom)

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

    def test_look_for_cnames_ptrs(self):
        name = "sucks1"
        a_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        a_dom.save()

        name = "adsfme1"
        c_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        c_dom.save()

        cn, _ = CNAME.objects.get_or_create(domain=c_dom, label="nddo",
                                            target="really.teebow.sucks1")
        cn.full_clean()
        cn.save()

        ptr = PTR(
            ip_str="128.193.2.1", name="seriously.teebow.sucks1", ip_type='4')
        ptr.full_clean()
        ptr.save()

        name = "teebow.sucks1"
        b_dom, _ = Domain.objects.get_or_create(name=name, delegated=False)
        b_dom.save()

        cn = CNAME.objects.get(pk=cn.pk)
        ptr = PTR.objects.get(pk=ptr.pk)
        self.assertTrue(cn.target_domain == b_dom)
        self.assertTrue(ptr.data_domain == b_dom)
        cn.label = "fooooobar"
        cn.full_clean()
        cn.save()

        # This is to hit some LOC for coverage purposes.

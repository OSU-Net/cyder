from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import create_zone

from basedomain import BaseDomain


class DomainTests(BaseDomain, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return reversed((
            Domain.objects.create(name='a'),
            Domain.objects.create(name='bbbbbbbbbb.a'),
            Domain.objects.create(name='c-c-c-c-c.a'),
            Domain.objects.create(name='d1d.bbbbbbbbbb.a'),
            Domain.objects.create(name='_foo.a'),
            Domain.objects.create(name='moo_foo._foo.a'),
        ))

    def test_master_domain(self):
        a = Domain.objects.create(name='a')
        self.assertEqual(a.master_domain, None)
        b = Domain.objects.create(name='b.a')
        self.assertEqual(b.master_domain, a)
        c = Domain.objects.create(name='c.b.a')
        self.assertEqual(c.master_domain, b)

    def test_soa_validators(self):
        m = Domain.objects.create(name='moo')
        f_m = Domain.objects.create(name='foo.moo')
        n_f_m = Domain.objects.create(name='noo.foo.moo')
        b_m = Domain.objects.create(name='baz.moo')

        s = SOA.objects.create(
            primary="ns1.foo.com", contact="asdf", description="test",
            root_domain=f_m)

        n_f_m = Domain.objects.get(pk=n_f_m.pk)  # Refresh object
        self.assertEqual(n_f_m.soa, s)

        s.root_domain = m
        s.save()

        b_m = Domain.objects.get(pk=b_m.pk)  # Refresh object
        self.assertEqual(b_m.soa, s)

        self.assertRaises(
            ValidationError, SOA.objects.create,
            primary="ns2.foo.com", contact="asdf", description="test2",
            root_domain=m)

    def test_2_soa_validators(self):
        d = Domain.objects.create(name="gaz")
        s1 = SOA.objects.create(
            primary="ns1.foo.gaz", contact="hostmaster.foo",
            description="foo.gaz2", root_domain=d)
        d1 = Domain.objects.create(name="foo.gaz")
        s1.root_domain = d1
        s1.save()

    def test_3_soa_validators(self):
        r = Domain.objects.create(name='9.in-addr.arpa')
        s1 = SOA.objects.create(
            primary="ns1.foo2.gaz", contact="hostmaster.foo",
            description="foo.gaz2", root_domain=r)

        Domain.objects.create(name="gaz")

    def test__name_to_master_domain(self):
        self.assertRaises(
            ValidationError, Domain.objects.create, name='foo.cn')

        Domain(name='cn').save()
        d = Domain.objects.create(name='foo.cn')
        self.assertRaises(
            ValidationError, Domain.objects.create, name='foo.cn')

    def test_create_domain(self):
        self.assertRaises(
            ValidationError, Domain.objects.create,
            name='foo.bar.oregonstate.edu')

    def test_remove_has_child_domain(self):
        Domain.objects.create(name='com')
        f_c = Domain.objects.create(name='foo.com')
        Domain.objects.create(name='boo.foo.com')
        self.assertRaises(ValidationError, f_c.delete)

    def test_invalid_add(self):
        bad_names = ('asfda.as df', '.', 'edu. ', '', '!@#$')

        for name in bad_names:
            self.assertRaises(
                ValidationError, Domain.objects.create, name=name)

    def test_remove_has_child_records(self):
        pass
        # Make sure deleting a domain doesn't leave stuff hanging.
        # TODO A records, Mx, TXT... all of the records!!

    def test_delegation_add_domain(self):
        boom = create_zone('boom')
        bleh = Domain.objects.create(name='bleh.boom', delegated=True)

        self.assertRaises(
            ValidationError, Domain.objects.create,
            name='baa.bleh.boom', delegated=False)

    def test_delegation(self):
        boom = create_zone('boom')
        bleh = Domain.objects.create(name='bleh.boom', delegated=True)
        self.ctnr.domains.add(bleh)

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
        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label="ns2", ctnr=self.ctnr, domain=bleh, ip_str="128.193.99.9",
            ip_type='4')

        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label="1000asdf", ctnr=self.ctnr, domain=bleh,
            target="asdf.asdf")

        # Editing should be allowed.
        arec = AddressRecord.objects.get(pk=arec.pk)
        arec.ip_str = "129.193.88.2"
        arec.save()

        # Adding new A records that have the same name as an NS should
        # be allowed.
        AddressRecord.objects.create(
            label="ns1", ctnr=self.ctnr, domain=bleh, ip_str="128.193.100.10",
            ip_type='4')

    def test_existing_record_new_domain(self):
        b_dom = Domain.objects.create(name='bo', delegated=False)
        t_dom = Domain.objects.create(name='to.bo', delegated=False)
        self.ctnr.domains.add(t_dom)

        AddressRecord.objects.create(
            label="no", ctnr=self.ctnr, domain=t_dom, ip_str="128.193.99.9",
            ip_type='4')

        self.assertRaises(
            ValidationError, Domain.objects.create,
            name='no.to.bo', delegated=False)

    def test_existing_cname_new_domain(self):
        b_dom = Domain.objects.create(name='bo', delegated=False)
        t_dom = Domain.objects.create(name='to.bo', delegated=False)
        self.ctnr.domains.add(t_dom)

        CNAME.objects.create(
            ctnr=self.ctnr, domain=t_dom, label="no", target="asdf")

        self.assertRaises(
            ValidationError, Domain.objects.create,
            name='no.to.bo', delegated=False)

    def test_rename_has_child_domain(self):
        a_dom = Domain.objects.create(name='sucks', delegated=False)

        b_dom = Domain.objects.create(name='django.sucks', delegated=False)

        c_dom = Domain.objects.create(name='adsfme', delegated=False)

        self.assertTrue(b_dom.master_domain == a_dom)

        try:
            c_dom.name = 'asdfme'
            c_dom.save()
        except:
            self.fail('Should be able to rename domain')

        a_dom.name = 'sucks2'
        self.assertRaises(ValidationError, a_dom.save)

from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin
from cyder.core.ctnr.models import Ctnr
from cyder.core.system.models import System
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.tests.utils import create_zone, DNSTest


class NSTestsModels(DNSTest, ModelTestMixin):
    def setUp(self):
        super(NSTestsModels, self).setUp()

        self.r = Domain.objects.create(name="ru")
        self.f_r = Domain.objects.create(name="foo.ru")
        self.b_f_r = Domain.objects.create(name="bar.foo.ru")
        Domain.objects.create(name="asdf")

        for d in (self.r, self.f_r, self.b_f_r):
            self.ctnr.domains.add(d)

        create_zone('128.in-addr.arpa')

        self.s = System.objects.create(name='test_system')

        self.net1 = Network.objects.create(network_str='128.193.0.0/17')
        self.sr1 = Range.objects.create(
            network=self.net1, range_type=STATIC, start_str='128.193.99.2',
            end_str='128.193.99.14')
        self.sr2 = Range.objects.create(
            network=self.net1, range_type=STATIC, start_str='128.193.1.1',
            end_str='128.193.1.14')

        self.net2 = Network.objects.create(network_str='14.10.1.0/30')
        self.sr3 = Range.objects.create(
            network=self.net2, range_type=STATIC, start_str='14.10.1.1',
            end_str='14.10.1.2')

        for r in (self.sr1, self.sr2, self.sr3):
            self.ctnr.ranges.add(r)

    def create_zone(self, name):
        domain = create_zone(name)
        self.ctnr.domains.add(domain)
        return domain

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            Nameserver.objects.create(
                domain=self.r, server='ns2.moot.ru'),
            Nameserver.objects.create(
                domain=self.r, server='ns5.moot.ru'),
            Nameserver.objects.create(
                domain=self.r, server=u'ns3.moot.ru'),
            Nameserver.objects.create(
                domain=self.b_f_r, server='n1.moot.ru'),
            Nameserver.objects.create(
                domain=self.b_f_r, server='ns2.moot.ru'),
            Nameserver.objects.create(
                domain=self.r, server='asdf.asdf'),
        )

    def test_add_invalid(self):
        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.f_r, server='ns3.foo.ru', ctnr=self.ctnr)

    def testtest_add_ns_in_domain(self):
        # Use an A record as a glue record.
        glue = AddressRecord.objects.create(
            label='ns2', ctnr=self.ctnr, domain=self.r, ip_str='128.193.1.10',
            ip_type='4')
        ns = Nameserver.objects.create(domain=self.r, server='ns2.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.server, ns.glue.fqdn)
        self.assertRaises(ValidationError, glue.delete)

        glue = AddressRecord.objects.create(
            label='ns3', ctnr=self.ctnr, domain=self.f_r,
            ip_str='128.193.1.10', ip_type='4')
        ns = Nameserver.objects.create(domain=self.f_r, server='ns3.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.server, ns.glue.fqdn)

    def test_disallow_name_update_of_glue_A(self):
        # Glue records should not be allowed to change their name.
        glue = AddressRecord.objects.create(
            label='ns39', ctnr=self.ctnr, domain=self.f_r,
            ip_str='128.193.1.77', ip_type='4')
        ns = Nameserver.objects.create(domain=self.f_r, server='ns39.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.glue, glue)

        glue.label = "ns22"
        self.assertRaises(ValidationError, glue.save)

    def test_disallow_name_update_of_glue_Intr(self):
        # Glue records should not be allowed to change their name.
        glue = StaticInterface.objects.create(
            label='ns24', domain=self.f_r, ctnr=self.ctnr,
            ip_str='128.193.99.10', ip_type='4', system=self.s,
            mac="11:22:33:44:55:66")
        ns = Nameserver.objects.create(domain=self.f_r, server='ns24.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.glue, glue)

        glue.label = "ns22"
        self.assertRaises(ValidationError, glue.save)

    def test_disallow_delete_of_glue_intr(self):
        # Interface glue records should not be allowed to be deleted.
        glue = StaticInterface.objects.create(
            label='ns24', domain=self.f_r, ctnr=self.ctnr,
            ip_str='128.193.99.10', ip_type='4', system=self.s,
            mac="11:22:33:44:55:66")
        ns = Nameserver.objects.create(domain=self.f_r, server='ns24.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.glue, glue)

        self.assertRaises(ValidationError, glue.delete)

    def test_manual_assign_of_glue(self):
        # Test that assigning a different glue record doesn't get overriden by
        # the auto assinging during the Nameserver's clean function.
        glue = StaticInterface.objects.create(
            label='ns25', domain=self.f_r, ctnr=self.ctnr,
            ip_str='128.193.99.10', ip_type='4', system=self.s,
            mac="11:22:33:44:55:66")
        ns = Nameserver.objects.create(domain=self.f_r, server='ns25.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.glue, glue)

        glue2 = AddressRecord.objects.create(
            label='ns25', ctnr=self.ctnr, domain=self.f_r,
            ip_str='128.193.1.78', ip_type='4')

        ns.full_clean()

        # Make sure things didn't get overridden.
        self.assertEqual(ns.glue, glue)

        ns.glue = glue2
        ns.save()
        # Refresh the object.
        ns = Nameserver.objects.get(pk=ns.pk)
        # Again, make sure things didn't get overridden.
        self.assertEqual(ns.glue, glue2)
        # Make sure we still can't delete.
        self.assertRaises(ValidationError, glue2.delete)
        self.assertRaises(ValidationError, ns.glue.delete)

        # We shuold be able to delete the other one.
        glue.delete()

    def testtest_add_ns_in_domain_intr(self):
        # Use an Interface as a glue record.
        glue = StaticInterface.objects.create(
            label='ns232', domain=self.r, ctnr=self.ctnr,
            ip_str='128.193.99.10', ip_type='4', system=self.s,
            mac="12:23:45:45:45:45")
        ns = Nameserver.objects.create(domain=self.r, server='ns232.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.server, ns.glue.fqdn)
        self.assertRaises(ValidationError, glue.delete)

        glue = StaticInterface.objects.create(
            label='ns332', domain=self.f_r, ctnr=self.ctnr,
            ip_str='128.193.1.10', ip_type='4', system=self.s,
            mac="11:22:33:44:55:66")
        ns = Nameserver.objects.create(domain=self.f_r, server='ns332.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.server, ns.glue.fqdn)

    def test_add_ns_outside_domain(self):
        ns = Nameserver.objects.create(domain=self.f_r, server='ns2.ru')
        self.assertFalse(ns.glue)

    def test_update_glue_to_no_intr(self):
        glue = StaticInterface.objects.create(
            label='ns34', domain=self.r, ctnr=self.ctnr, ip_str='128.193.1.10',
            ip_type='4', system=self.s, mac="11:22:33:44:55:66")
        data = {'domain': self.r, 'server': 'ns34.ru'}
        ns = Nameserver.objects.create(domain=self.r, server='ns34.ru')
        self.assertTrue(ns.glue)

        ns.server = "ns4.wee"
        ns.save()
        self.assertTrue(ns.glue is None)

    def test_update_glue_record_intr(self):
        # Glue records can't change their name.
        glue = StaticInterface.objects.create(
            label='ns788', domain=self.r, ctnr=self.ctnr,
            ip_str='128.193.1.10', ip_type='4', system=self.s,
            mac="11:22:33:44:55:66")
        ns = Nameserver.objects.create(domain=self.r, server='ns788.ru')
        self.assertTrue(ns.glue)
        glue.label = "asdfasdf"
        self.assertRaises(ValidationError, glue.save)

    def test_update_glue_to_no_glue(self):
        glue = AddressRecord.objects.create(
            label='ns3', ctnr=self.ctnr, domain=self.r, ip_str='128.193.1.10',
            ip_type='4')
        ns = Nameserver.objects.create(domain=self.r, server='ns3.ru')
        self.assertTrue(ns.glue)

        ns.server = "ns4.wee"
        ns.save()
        self.assertTrue(ns.glue is None)

    def test_delete_ns(self):
        glue = AddressRecord.objects.create(
            label='ns4', ctnr=self.ctnr, domain=self.f_r,
            ip_str='128.196.1.10', ip_type='4')
        ns = Nameserver.objects.create(domain=self.f_r, server='ns4.foo.ru')
        self.assertTrue(ns.glue)
        self.assertEqual(ns.server, ns.glue.fqdn)

        ns.delete()

        self.assertFalse(Nameserver.objects.filter(
            server='ns2.foo.ru', domain=self.f_r).exists())

    def test_invalid_create(self):
        glue = AddressRecord.objects.create(
            label='ns2', ctnr=self.ctnr, domain=self.r, ip_str='128.193.1.10',
            ip_type='4')
        glue.save()

        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.r, server='ns2 .ru', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.r, server='ns2$.ru', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.r, server='ns2..ru', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.r, server='ns2.ru ', ctnr=self.ctnr)

        self.assertRaises(
            ValidationError, Nameserver.objects.create,
            domain=self.r, server='', ctnr=self.ctnr)

    def test_add_dup(self):
        def x():
            Nameserver.objects.create(domain=self.r, server='ns2.moot.ru')

        x()
        self.assertRaises(ValidationError, x)

    def _get_post_data(self, random_str):
        """Return a valid set of data"""
        return {
            'root_domain': '{0}.oregonstate.com'.format(random_str),
            'soa_primary': 'ns1.oregonstate.com',
            'soa_contact': 'noc.oregonstate.com',
            'nameserver_1': 'ns1.oregonstate.com',
            'ttl_1': '1234'
        }

    def test_bad_nameserver_soa_state_case_1_0(self):
        # This is Case 1
        root_domain = self.create_zone('asdf10.asdf')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        # At this point we should have a domain at the root of a zone with no
        # other records in it.

        # Adding a record shouldn't be allowed because there is no NS record on
        # the zone's root domain.
        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label='', ctnr=self.ctnr, domain=root_domain, ip_type="6",
            ip_str="1::")

        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label='', ctnr=self.ctnr, domain=root_domain, target="asdf")

    def test_bad_nameserver_soa_state_case_1_1(self):
        # This is Case 1
        root_domain = self.create_zone('asdf111.asdf')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        # At this point we should have a domain at the root of a zone with no
        # other records in it.

        # Let's create a child domain and try to add a record there.
        cdomain = Domain.objects.create(name="test." + root_domain.name)

        # Adding a record shouldn't be allowed because there is no NS record on
        # the zone's root domain.
        self.assertRaises(
            ValidationError, AddressRecord.objects.create,
            label='', ctnr=self.ctnr, domain=cdomain, ip_type="6",
            ip_str="1::")
        self.assertRaises(
            ValidationError, CNAME.objects.create,
            label='', ctnr=self.ctnr, domain=cdomain, target="asdf")

    def test_bad_nameserver_soa_state_case_1_2(self):
        # This is Case 1 ... with ptr's
        root_domain = self.create_zone('12.in-addr.arpa')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        # At this point we should have a domain at the root of a zone with no
        # other records in it.

        # Adding a record shouldn't be allowed because there is no NS record on
        # the zone's root domain.
        self.assertRaises(
            ValidationError, PTR.objects.create,
            ctnr=self.ctnr, fqdn="asdf", ip_str="12.10.1.1", ip_type="4")

    def test_bad_nameserver_soa_state_case_1_3(self):
        # This is Case 1 ... with ptr's
        root_domain = self.create_zone('13.in-addr.arpa')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        # At this point we should have a domain at the root of a zone with no
        # other records in it.

        # Let's create a child domain and try to add a record there.
        cdomain = Domain.objects.create(name="10.13.in-addr.arpa")

        # Adding a record shouldn't be allowed because there is no NS record on
        # the zone's root domain.
        self.assertRaises(
            ValidationError, PTR.objects.create,
            ctnr=self.ctnr, fqdn="asdf", ip_str="13.10.1.1", ip_type="4")

    def test_bad_nameserver_soa_state_case_1_4(self):
        # This is Case 1 ... with StaticInterfaces's
        reverse_root_domain = self.create_zone('14.in-addr.arpa')
        root_domain = self.create_zone('asdf14.asdf')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        # At this point we should have a domain at the root of a zone with no
        # other records in it.

        # Let's create a child domain and try to add a record there.
        cdomain = Domain.objects.create(name="10.14.in-addr.arpa")

        # Adding a record shouldn't be allowed because there is no NS record on
        # the zone's root domain.
        self.assertRaises(
            ValidationError, StaticInterface.objects.create,
            label="asdf", domain=root_domain, ip_str="14.10.1.1", ip_type="4",
            mac="11:22:33:44:55:66", system=self.s, ctnr=self.ctnr)

    # See record.tests for the case a required view is deleted.
    def test_bad_nameserver_soa_state_case_2_0(self):
        # This is Case 2
        root_domain = self.create_zone('asdf20.asdf')
        self.assertEqual(root_domain.nameserver_set.count(), 1)
        ns = root_domain.nameserver_set.all()[0]

        # At this point we should have a domain at the root of a zone with one
        # NS record associated to the domain.

        AddressRecord.objects.create(
            label='', ctnr=self.ctnr, domain=root_domain, ip_type="6",
            ip_str="1::")

        self.assertRaises(ValidationError, ns.delete)

    def test_bad_nameserver_soa_state_case_2_1(self):
        # This is Case 2
        root_domain = self.create_zone('asdf21.asdf')
        self.assertEqual(root_domain.nameserver_set.count(), 1)
        ns = root_domain.nameserver_set.all()[0]

        # At this point we should have a domain at the root of a zone with one
        # NS record associated to the domain.

        # Let's create a child domain and add a record there, then try to
        # delete the NS record
        cdomain = Domain.objects.create(name="test." + root_domain.name)
        self.ctnr.domains.add(cdomain)

        AddressRecord.objects.create(
            label='', ctnr=self.ctnr, domain=cdomain, ip_type="6",
            ip_str="1::")

        self.assertRaises(ValidationError, ns.delete)

    def test_bad_nameserver_soa_state_case_2_2(self):
        # This is Case 2 ... with PTRs
        root_domain = self.create_zone('14.in-addr.arpa')
        self.assertEqual(root_domain.nameserver_set.count(), 1)
        ns = root_domain.nameserver_set.all()[0]

        # At this point we should have a domain at the root of a zone with one
        # NS record associated to the domain.

        PTR.objects.create(
            ctnr=self.ctnr, fqdn="bloo.asdf", ip_str="14.10.1.1", ip_type="4")

        self.assertRaises(ValidationError, ns.delete)

    def test_bad_nameserver_soa_state_case_2_3(self):
        # This is Case 2 ... with PTRs
        Domain.objects.create(name='14.in-addr.arpa')
        root_domain = self.create_zone('10.14.in-addr.arpa')
        self.assertEqual(root_domain.nameserver_set.count(), 1)
        ns = root_domain.nameserver_set.all()[0]

        # At this point we should have a domain at the root of a zone with one
        # NS record associated to the domain.

        # Let's create a child domain and add a record there, then try to
        # delete the NS record.
        cdomain = Domain.objects.create(name="test." + root_domain.name)

        PTR.objects.create(
            ctnr=self.ctnr, fqdn="bloo.asdf", ip_str="14.10.1.1", ip_type="4")

        self.assertRaises(ValidationError, ns.delete)

    def test_bad_nameserver_soa_state_case_3_0(self):
        # This is Case 3
        root_domain = self.create_zone('asdf30.asdf')
        for ns in root_domain.nameserver_set.all():
            ns.delete()
        ns.domain.soa.delete()
        root_domain = Domain.objects.get(pk=root_domain.pk)

        # At this point we should have a domain pointed at no SOA record with
        # no records attached to it. It also has no child domains.

        # Add a record to the domain.
        AddressRecord.objects.create(
            label='', ctnr=self.ctnr, domain=root_domain, ip_type="6",
            ip_str="1::")

        self.assertRaises(
            ValidationError, SOA.objects.create,
            primary="asdf.asdf", contact="asdf.asdf", description="asdf",
            root_domain=root_domain)

    def test_bad_nameserver_soa_state_case_3_1(self):
        # This is Case 3
        root_domain = self.create_zone('asdf31.asdf')

        # Try case 3 but add a record to a child domain of root_domain.
        bad_root_domain = Domain.objects.create(
            name="below." + root_domain.name)
        cdomain = Domain.objects.create(name="test." + bad_root_domain.name)
        self.ctnr.domains.add(cdomain)

        # Add a record to the domain.
        AddressRecord.objects.create(
            label='', ctnr=self.ctnr, domain=cdomain, ip_type="6",
            ip_str="1::")

        # Now try to add the domain to the zone that has no NS records at its
        # root.
        self.assertRaises(
            ValidationError, SOA.objects.create,
            root_domain=bad_root_domain, contact="a", primary='b')

    def test_bad_nameserver_soa_state_case_3_2(self):
        # This is Case 3 ... with PTRs
        root_domain = create_zone('14.in-addr.arpa')
        for ns in root_domain.nameserver_set.all():
            ns.delete()

        root_domain.soa.delete()
        root_domain = Domain.objects.get(pk=root_domain.pk)
        self.assertIsNone(root_domain.soa)

        # At this point we should have a domain pointed at no SOA record with
        # no records attached to it. It also has no child domains.

        # Add a record to the domain.

        self.assertRaises(
            ValidationError, PTR.objects.create,
            ctnr=self.ctnr, fqdn="bloo.asdf", ip_str="14.10.1.1", ip_type="4")

    def test_bad_nameserver_soa_state_case_3_3(self):
        # This is Case 3 ... with PTRs
        root_domain = create_zone('14.in-addr.arpa')

        bad_root_domain = Domain.objects.create(name="10." + root_domain.name)
        cdomain = Domain.objects.create(name="1.10.14.in-addr.arpa")

        PTR.objects.create(
            fqdn=('eh.' + cdomain.name), ctnr=self.ctnr, ip_type="4",
            ip_str="14.10.1.1")

        # Now try to add the domain to the zone that has no NS records at its
        # root.
        self.assertRaises(
            ValidationError, SOA.objects.create,
            root_domain=bad_root_domain, contact="a", primary='b')

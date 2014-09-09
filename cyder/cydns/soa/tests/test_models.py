"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.cydns.soa.models import SOA
from cyder.cydns.domain.models import Domain


class SOATests(TestCase):
    def setUp(self):
        pass

    def do_generic_add(self, primary, contact, retry, refresh, description):
        d = Domain.objects.create(name=description)
        soa = SOA(primary=primary, contact=contact, root_domain=d,
                  retry=retry, refresh=refresh, description=description)
        soa.save()
        soa.save()
        rsoa = SOA.objects.filter(primary=primary, contact=contact,
                                  retry=retry, refresh=refresh)
        self.assertTrue(len(rsoa) == 1)
        return soa

    def test_add_soa(self):
        primary = "ns1.oregonstate.edu"
        contact = "admin.oregonstate.edu"
        retry = 1234
        refresh = 1234123
        description = "bluh"
        self.do_generic_add(primary, contact, retry, refresh,
                            description=description)
        soa = SOA.objects.filter(primary=primary, contact=contact,
                                 retry=retry, refresh=refresh)
        soa[0].save()
        self.assertTrue(soa)
        soa[0].__repr__()
        soa = soa[0]
        self.assertTrue(soa.details())

        primary = "do.com"
        contact = "admf.asdf"
        retry = 432152
        refresh = 1235146134
        description = "bloh"
        self.do_generic_add(primary, contact, retry, refresh,
                            description=description)
        soa = SOA.objects.filter(primary=primary, contact=contact,
                                 retry=retry, refresh=refresh)
        self.assertTrue(soa)
        soa = soa[0]
        self.assertTrue(soa.details())

        primary = "ns1.derp.com"
        contact = "admf.asdf"
        d = Domain.objects.create(name="bwah")
        soa = SOA(primary=primary, contact=contact, root_domain=d)
        soa.save()
        self.assertTrue(
            soa.serial and soa.expire and soa.retry and soa.refresh)
        self.assertTrue(soa.details())

    def test_add_remove(self):
        primary = "ns2.oregonstate.edu"
        contact = "admin.oregonstate.edu"
        retry = 1234
        refresh = 1234123
        description = "bluk"
        soa = self.do_generic_add(
            primary, contact, retry, refresh, description=description)
        soa.delete()
        soa = SOA.objects.filter(primary=primary, contact=contact,
                                 retry=retry, refresh=refresh)
        self.assertTrue(len(soa) == 0)

        primary = "dddo.com"
        contact = "admf.asdf"
        retry = 432152
        refresh = 1235146134
        description = "blook"
        soa = self.do_generic_add(
            primary, contact, retry, refresh, description=description)
        soa.delete()
        soa = SOA.objects.filter(primary=primary, contact=contact, retry=retry,
                                 refresh=refresh, description=description)
        self.assertTrue(len(soa) == 0)

        # Add dup
        description = "blork"
        soa = self.do_generic_add(
            primary, contact, retry, refresh, description=description)
        soa.save()
        self.assertRaises(ValidationError, self.do_generic_add, *(
            primary, contact, retry, refresh, description))

    def test_add_invalid(self):
        data = {'primary': "daf..fff", 'contact': "foo.com"}
        soa = SOA(**data)
        self.assertRaises(ValidationError, soa.save)
        data = {'primary': 'foo.com', 'contact': 'dkfa..'}
        soa = SOA(**data)
        self.assertRaises(ValidationError, soa.save)
        data = {'primary': 'adf', 'contact': '*@#$;'}
        soa = SOA(**data)
        self.assertRaises(ValidationError, soa.save)

    def test_chain_soa_domain_add(self):
        d0 = Domain(name='com')
        d0.save()
        data = {'primary': "ns1.foo.com", 'contact': "email.foo.com",
                'root_domain':d0}
        soa = SOA(**data)
        soa.save()
        d1 = Domain(name='foo.com', soa=soa)
        d1.save()
        self.assertTrue(soa == d1.soa)
        d2 = Domain(name='bar.foo.com', soa=soa)
        d2.save()
        self.assertTrue(soa == d2.soa)
        d3 = Domain(name='new.foo.com', soa=soa)
        d3.save()
        self.assertTrue(soa == d3.soa)
        d4 = Domain(name='far.bar.foo.com', soa=soa)
        d4.save()
        self.assertTrue(soa == d4.soa)
        d5 = Domain(name='tee.new.foo.com', soa=soa)
        d5.save()
        self.assertTrue(soa == d5.soa)
        d5.delete()
        d4.delete()
        self.assertTrue(soa == d1.soa)
        self.assertTrue(soa == d2.soa)
        self.assertTrue(soa == d3.soa)

    def test_nested_zones(self):
        self.domain_names = (
            'y', 'x.y', 'p.x.y', 'q.x.y',
            'a.q.x.y', 'b.q.x.y', 'c.q.x.y')
        for name in self.domain_names:
            d = Domain(name=name)
            d.save()

        soa_q_x_y = SOA(
            root_domain=Domain.objects.get(name='q.x.y'),
            primary='bleh1', contact='bleh1')
        soa_q_x_y.save()

        for name in ('y', 'x.y', 'p.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, None)
        for name in ('q.x.y', 'a.q.x.y', 'b.q.x.y', 'c.q.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, soa_q_x_y)

        soa_x_y = SOA(
            root_domain=Domain.objects.get(name='x.y'),
            primary='bleh2', contact='bleh2')
        soa_x_y.save()

        soa_q_x_y = SOA.objects.get(root_domain__name='q.x.y')

        self.assertEqual(Domain.objects.get(name='y').soa, None)
        for name in ('x.y', 'p.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, soa_x_y)
        for name in ('q.x.y', 'a.q.x.y', 'b.q.x.y', 'c.q.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, soa_q_x_y)

        soa_q_x_y.delete()

        soa_x_y = SOA.objects.get(root_domain__name='x.y')

        self.assertEqual(Domain.objects.get(name='y').soa, None)
        for name in ('x.y', 'p.x.y', 'q.x.y', 'a.q.x.y', 'b.q.x.y', 'c.q.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, soa_x_y)

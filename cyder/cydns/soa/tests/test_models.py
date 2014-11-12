from django.core.exceptions import ValidationError

from cyder.base.tests import ModelTestMixin, TestCase
from cyder.cydns.soa.models import SOA
from cyder.cydns.domain.models import Domain


class SOATests(TestCase, ModelTestMixin):
    @property
    def objs(self):
        """Create objects for test_create_delete."""
        d1 = Domain.objects.create(name='marp')
        d2 = Domain.objects.create(name='blook')
        d3 = Domain.objects.create(name='bluh')
        d4 = Domain.objects.create(name='wep')
        d5 = Domain.objects.create(name='blah')
        return (
            SOA.objects.create(
                primary="ns2.oregonstate.edu", contact="admin.oregonstate.edu",
                retry=1234, refresh=1234123, description="marp",
                root_domain=d1),
            SOA.objects.create(
                primary="dddo.com", contact="admf.asdf", retry=432152,
                refresh=1235146134, description="blook", root_domain=d2),
            SOA.objects.create(
                primary="ns1.oregonstate.edu", contact="admin.oregonstate.edu",
                retry=1234, refresh=1234123, description="bluh",
                root_domain=d3),
            SOA.objects.create(
                primary="do.com", contact="admf.asdf", retry=432152,
                refresh=1235146134, description="wep", root_domain=d4),
            SOA.objects.create(
                primary='ns1.derp.com', contact='admf.asdf', root_domain=d5),
        )

    def test_duplicate(self):
        d = Domain.objects.create(name='flop')

        SOA.objects.create(
            primary='hoo.ha', contact='me', retry=100009,
            refresh=2003, description='flippy', root_domain=d)

        # Same root_domain.
        self.assertRaises(
            ValidationError, SOA.objects.create, primary='hee.ha',
            contact='you', retry=40404, refresh=10038, description='floppy',
            root_domain=d)

    def test_add_invalid(self):
        self.assertRaises(
            ValidationError, SOA.objects.create, primary='daf..fff',
            contact='foo.com')

        self.assertRaises(
            ValidationError, SOA.objects.create, primary='foo.com',
            contact='dkfa..')

        self.assertRaises(
            ValidationError, SOA.objects.create, primary='adf',
            contact='*@#$;')

    def test_chain_soa_domain_add(self):
        d0 = Domain.objects.create(name='com')
        soa = SOA.objects.create(
            primary='ns1.foo.com', contact='email.foo.com', root_domain=d0)

        d1 = Domain.objects.create(name='foo.com')
        self.assertEqual(soa, d1.soa)

        d2 = Domain.objects.create(name='bar.foo.com')
        self.assertEqual(soa, d2.soa)

        d3 = Domain.objects.create(name='new.foo.com')
        self.assertEqual(soa, d3.soa)

        d4 = Domain.objects.create(name='far.bar.foo.com')
        self.assertEqual(soa, d4.soa)

        d5 = Domain.objects.create(name='tee.new.foo.com')
        self.assertEqual(soa, d5.soa)

        d5.delete()
        d4.delete()
        self.assertEqual(soa, d1.soa)
        self.assertEqual(soa, d2.soa)
        self.assertEqual(soa, d3.soa)

    def test_nested_zones(self):
        self.domain_names = (
            'y', 'x.y', 'p.x.y', 'q.x.y',
            'a.q.x.y', 'b.q.x.y', 'c.q.x.y')
        for name in self.domain_names:
            d = Domain.objects.create(name=name)

        soa_q_x_y = SOA.objects.create(
            root_domain=Domain.objects.get(name='q.x.y'),
            primary='bleh1', contact='bleh1')

        for name in ('y', 'x.y', 'p.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, None)
        for name in ('q.x.y', 'a.q.x.y', 'b.q.x.y', 'c.q.x.y'):
            self.assertEqual(Domain.objects.get(name=name).soa, soa_q_x_y)

        soa_x_y = SOA.objects.create(
            root_domain=Domain.objects.get(name='x.y'),
            primary='bleh2', contact='bleh2')

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

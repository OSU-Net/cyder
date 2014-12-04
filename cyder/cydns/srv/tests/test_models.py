from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.core.ctnr.models import Ctnr
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain

from cyder.core.ctnr.models import Ctnr


class SRVTests(TestCase):
    def setUp(self):
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')
        self.o = Domain.objects.create(name="org")
        self.o_e = Domain.objects.create(name="oregonstate.org")
        self.b_o_e = Domain.objects.create(name="bar.oregonstate.org")
        for dom in (self.o, self.o_e, self.b_o_e):
            self.ctnr.domains.add(dom)

    def create_srv(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        return SRV.objects.create(**kwargs)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return [
            self.create_srv(
                label='_df', domain=self.o_e, target='relay.oregonstate.edu',
                priority=2, weight=2222, port=222),
            self.create_srv(
                label='_df', domain=self.o, target='foo.com.nar',
                priority=1234, weight=23414, port=222),
            self.create_srv(
                label='_sasfd', domain=self.b_o_e, target='foo.safasdlcom.nar',
                priority=12234, weight=23414, port=222),
            self.create_srv(
                label='_faf', domain=self.o, target='foo.com.nar',
                priority=1234, weight=23414, port=222),
            self.create_srv(
                label='_bar', domain=self.o_e, target='relay.oregonstate.edu',
                priority=2, weight=2222, port=222),
            self.create_srv(
                label='_bar', domain=self.o_e, target='', priority=2,
                weight=2222, port=222),
        ]

    def test_invalid_add_update(self):
        def create_srv():
            return self.create_srv(
                label='_df', domain=self.o_e, target='relay.oregonstate.edu',
                priority=2, weight=2222, port=222)

        srv = create_srv()
        self.assertRaises(ValidationError, create_srv)

        self.create_srv(
            label='_df', domain=self.o_e, target='foo.oregonstate.edu',
            priority=2, weight=2222, port=222)

        srv.target = "foo.oregonstate.edu"
        self.assertRaises(ValidationError, srv.save)

        srv.port = 65536
        self.assertRaises(ValidationError, srv.save)

        srv.port = 1
        srv.priority = 65536
        self.assertRaises(ValidationError, srv.save)

        srv.priority = 1
        srv.weight = 65536
        self.assertRaises(ValidationError, srv.save)

        srv.target = "asdfas"
        srv.label = "no_first"
        self.assertRaises(ValidationError, srv.save)

        srv.target = "_df"
        self.assertRaises(ValidationError, srv.save)

    def test_domain_ctnr(self):
        """Test that an SRV's domain must be in the SRV's container"""
        ctnr1 = Ctnr.objects.create(name='test_ctnr1')
        ctnr1.domains.add(self.o_e)

        ctnr2 = Ctnr.objects.create(name='test_ctnr2')

        SRV.objects.create(
            label='_foo', domain=self.o_e, target='bar.oregonstate.edu',
            priority=1, weight=100, port=9002, ctnr=ctnr1)

        self.assertRaises(
            ValidationError, SRV.objects.create, label='_bleh',
            domain=self.o_e, target='xyz.oregonstate.edu', priority=1,
            weight=100, port=9002, ctnr=ctnr2)

    def test_name_unique(self):
        """Test that two SRVs cannot share a name"""
        srv1 = SRV(label='_foo', domain=self.o_e, target='bar.oregonstate.edu',
                   priority=1, weight=100, port=9002, ctnr=self.ctnr)
        srv1.save()

        self.assertRaises(
            ValidationError, SRV.objects.create, label='_foo', domain=self.o_e,
            target='bleh.oregonstate.edu', priority=1, weight=100, port=9002)

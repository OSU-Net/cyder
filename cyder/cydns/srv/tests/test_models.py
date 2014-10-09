from django.test import TestCase
from django.core.exceptions import ValidationError

from cyder.core.ctnr.models import Ctnr
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain

from cyder.core.ctnr.models import Ctnr


class SRVTests(TestCase):
    def setUp(self):
        self.ctnr = Ctnr(name='abloobloobloo')
        self.ctnr.save()
        self.o = Domain(name="org")
        self.o.save()
        self.o_e = Domain(name="oregonstate.org")
        self.o_e.save()
        self.b_o_e = Domain(name="bar.oregonstate.org")
        self.b_o_e.save()
        for dom in [self.o, self.o_e, self.b_o_e]:
            self.ctnr.domains.add(dom)

    def do_generic_add(self, **data):
        data['ctnr'] = self.ctnr
        srv = SRV(**data)
        srv.save()
        srv.__repr__()
        self.assertTrue(srv.details())
        rsrv = SRV.objects.filter(**data)
        self.assertTrue(len(rsrv) == 1)
        return srv

    def do_remove(self, **data):
        srv = self.do_generic_add(**data)
        srv.delete()
        rsrv = SRV.objects.filter(**data)
        self.assertTrue(len(rsrv) == 0)

    def test_add_remove_srv(self):
        data = {'label': '_df', 'domain': self.o_e,
                'target': 'relay.oregonstate.edu', 'priority': 2, 'weight':
                2222, 'port': 222}
        self.do_remove(**data)
        data = {'label': '_df', 'domain': self.o, 'target':
                'foo.com.nar', 'priority': 1234, 'weight': 23414, 'port': 222}
        self.do_remove(**data)
        data = {'label': '_sasfd', 'domain': self.b_o_e,
                'target': 'foo.safasdlcom.nar', 'priority': 12234, 'weight':
                23414, 'port': 222}
        self.do_remove(**data)
        data = {'label': '_faf', 'domain': self.o, 'target':
                'foo.com.nar', 'priority': 1234, 'weight': 23414, 'port': 222}
        self.do_remove(**data)

        data = {'label': '_bar', 'domain': self.o_e, 'target':
                'relay.oregonstate.edu', 'priority': 2, 'weight': 2222, 'port':
                222}
        self.do_remove(**data)

        data = {'label': '_bar', 'domain': self.o_e, 'target':
                '', 'priority': 2, 'weight': 2222, 'port':
                222}
        self.do_remove(**data)

    def test_invalid_add_update(self):
        data = {'label': '_df', 'domain': self.o_e,
                'target': 'relay.oregonstate.edu', 'priority': 2, 'weight':
                2222, 'port': 222}
        srv0 = self.do_generic_add(**data)
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {
            'label': '_df', 'domain': self.o_e,
            'target': 'foo.oregonstate.edu', 'priority': 2, 'weight': 2222,
            'port': 222}

        self.do_generic_add(**data)
        self.assertRaises(ValidationError, self.do_generic_add, **data)

        srv0.target = "foo.oregonstate.edu"
        self.assertRaises(ValidationError, srv0.save)

        srv0.port = 65536
        self.assertRaises(ValidationError, srv0.save)

        srv0.port = 1
        srv0.priority = 65536
        self.assertRaises(ValidationError, srv0.save)

        srv0.priority = 1
        srv0.weight = 65536
        self.assertRaises(ValidationError, srv0.save)

        srv0.target = "asdfas"
        srv0.label = "no_first"
        self.assertRaises(ValidationError, srv0.save)

        srv0.target = "_df"
        self.assertRaises(ValidationError, srv0.save)

    def test_domain_ctnr(self):
        """Test that an SRV's domain must be in the SRV's container"""
        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.save()

        srv1 = SRV(label='_foo', domain=self.o_e, target='bar.oregonstate.edu',
                   priority=1, weight=100, port=9002, ctnr=ctnr1)
        srv1.save()

        with self.assertRaises(ValidationError):
            srv2 = SRV(label='_bleh', domain=self.o_e,
                       target='xyz.oregonstate.edu', priority=1, weight=100,
                       port=9002, ctnr=ctnr2)
            srv2.save()

    def test_name_unique(self):
        """Test that two SRVs cannot share a name"""
        srv1 = SRV(label='_foo', domain=self.o_e, target='bar.oregonstate.edu',
                priority=1, weight=100, port=9002, ctnr=self.ctnr)
        srv1.save()

        with self.assertRaises(ValidationError):
            srv2 = SRV(label='_foo', domain=self.o_e,
                       target='bleh.oregonstate.edu', priority=1, weight=100,
                       port=9002)
            srv2.save()

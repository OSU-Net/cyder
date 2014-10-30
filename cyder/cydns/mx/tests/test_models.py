from django.core.exceptions import ValidationError

import cyder.base.tests
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.txt.models import TXT


class MXTests(cyder.base.tests.TestCase):
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
        mx = MX(**data)
        mx.__repr__()
        mx.save()
        self.assertTrue(mx.details())
        rmx = MX.objects.filter(**data)
        self.assertTrue(len(rmx) == 1)
        return mx

    def test_add_mx(self):
        data = {'label': 'osumail', 'domain': self.o, 'server':
                'relay.oregonstate.edu', 'priority': 2, 'ttl': 2222}
        self.do_generic_add(**data)
        data = {'label': '', 'domain': self.o_e, 'server':
                'mail.sdf.fo', 'priority': 9, 'ttl': 34234}
        self.do_generic_add(**data)
        data = {'label': 'mail', 'domain': self.b_o_e, 'server':
                'asdf.asdf', 'priority': 123, 'ttl': 213}
        self.do_generic_add(**data)
        data = {'label': '', 'domain': self.b_o_e, 'server':
                'oregonstate.edu', 'priority': 2, 'ttl': 2}
        self.do_generic_add(**data)
        data = {'label': u'dsfasdfasdfasdfasdfasdfasdf', 'domain':
                self.o, 'server': 'nope.mail', 'priority': 12, 'ttl': 124}
        self.do_generic_add(**data)

    def test_add_invalid(self):
        data = {'label': '', 'domain': self.o, 'server':
                'mail.oregonstate.edu', 'priority': 123, 'ttl': 23}
        self.assertRaises(
            ValidationError, self.do_generic_add, **data)  # TLD condition
        data = {'label': 'adsf,com', 'domain': self.o_e,
                'server': 'mail.oregonstate.edu', 'priority': 123, 'ttl': 23}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': 'foo', 'domain': self.o_e, 'server':
                'mail..com', 'priority': 34, 'ttl': 1234}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': 'foo.bar', 'domain': self.o_e, 'server':
                'mail.com', 'priority': 3, 'ttl': 23424}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': "asdf#$@", 'domain': self.o_e, 'server':
                'coo.com', 'priority': 123, 'ttl': 23}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': "asdf", 'domain': self.o_e, 'server':
                'coo.com', 'priority': -1, 'ttl': 23}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': "asdf", 'domain': self.o_e, 'server':
                'coo.com', 'priority': 65536, 'ttl': 23}
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': "asdf", 'domain': self.o_e, 'server':
                234, 'priority': 65536, 'ttl': 23}
        self.assertRaises(ValidationError, self.do_generic_add, **data)

        data = {'label': "a", 'domain': self.o_e, 'server':
                'foo', 'priority': 6556, 'ttl': 91234241254}
        self.assertRaises(ValidationError, self.do_generic_add, **data)

    def do_remove(self, **data):
        mx = self.do_generic_add(**data)
        mx.delete()
        rmx = MX.objects.filter(**data)
        self.assertTrue(len(rmx) == 0)

    def test_remove(self):
        data = {'label': '', 'domain': self.o_e, 'server':
                'frelay.oregonstate.edu', 'priority': 2, 'ttl': 2222}
        self.do_remove(**data)
        data = {'label': '', 'domain': self.o_e, 'server':
                'fmail.sdf.fo', 'priority': 9, 'ttl': 34234}
        self.do_remove(**data)
        data = {'label': 'mail', 'domain': self.b_o_e, 'server':
                'asdff.asdf', 'priority': 123, 'ttl': 213}
        self.do_remove(**data)
        data = {'label': '', 'domain': self.b_o_e, 'server':
                'oregonsftate.edu', 'priority': 2, 'ttl': 2}
        self.do_remove(**data)
        data = {'label': u'dsfasdfasdfasdfasdfasdfasdf', 'domain':
                self.o, 'server': 'nopef.mail', 'priority': 12, 'ttl': 124}
        self.do_remove(**data)

    def test_add_and_update_dup(self):
        data = {'label': '', 'domain': self.o_e, 'server':
                'relaydf.oregonstate.edu', 'priority': 2, 'ttl': 2222}
        mx0 = self.do_generic_add(**data)
        self.assertRaises(ValidationError, self.do_generic_add, **data)
        data = {'label': '', 'domain': self.o_e, 'server':
                'mail.sddf.fo', 'priority': 9, 'ttl': 34234}
        mx1 = self.do_generic_add(**data)
        self.assertRaises(ValidationError, self.do_generic_add, **data)

        mx0.server = "mail.sddf.fo"
        mx0.priority = 9
        mx0.ttl = 34234
        self.assertRaises(ValidationError, mx0.save)

    def test_add_with_cname(self):
        label = "cnamederp"
        domain = self.o_e
        data = "foo.com"
        cn = CNAME(label=label, ctnr=self.ctnr, domain=domain, target=data)
        cn.save()

        data = {'label': '', 'domain': self.o_e, 'server':
                'cnamederp.oregonstate.org', 'priority': 2, 'ttl': 2222}
        with self.assertRaises(ValidationError):
            self.do_generic_add(**data)

    def test_domain_ctnr(self):
        """Test that an MX's domain must be in the MX's container"""
        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.save()

        mx1 = MX(label='foo', domain=self.o_e, server='bar.oregonstate.edu',
                 priority=1, ttl=1000, ctnr=ctnr1)
        mx1.save()

        with self.assertRaises(ValidationError):
            mx1 = MX(label='bleh', domain=self.o_e,
                     server='xyz.oregonstate.edu', priority=1, ttl=1000,
                     ctnr=ctnr2)
            mx1.save()

    def test_name_unique(self):
        """Test that two MXs cannot share a name"""
        mx1 = MX(label='foo', domain=self.o_e, server='bar.oregonstate.edu',
                 priority=1, ttl=1000, ctnr=self.ctnr)
        mx1.save()

        with self.assertRaises(ValidationError):
            mx2 = MX(label='foo', domain=self.o_e,
                     server='bleh.oregonstate.edu', priority=1, ttl=1000)
            mx2.save()

    def test_sshfp_txt_name(self):
        """Test that an MX can share a name with an SSHFP or a TXT"""
        def create_mx():
            mx = MX(label='foo', domain=self.o_e, server='bar.oregonstate.edu',
                    priority=1, ttl=1000, ctnr=self.ctnr)
            mx.save()
            return mx
        create_mx.name = 'MX'

        def create_sshfp():
            s = SSHFP(label='foo', domain=self.o_e,
                      key='7d97e98f8af710c7e7fe703abc8f639e0ee507c4',
                      algorithm_number=1, fingerprint_type=1, ctnr=self.ctnr)
            s.save()
            return s
        create_sshfp.name = 'SSHFP'

        def create_txt():
            t = TXT(label='foo', domain=self.o_e, txt_data='Hi, Mom!',
                    ctnr=self.ctnr)
            t.save()
            return t
        create_txt.name = 'TXT'

        self.assertObjectsDontConflict((create_mx, create_sshfp, create_txt))

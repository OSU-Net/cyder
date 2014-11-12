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
        self.ctnr = Ctnr.objects.create(name='abloobloobloo')
        self.o = Domain.objects.create(name="org")
        self.o_e = Domain.objects.create(name="oregonstate.org")
        self.b_o_e = Domain.objects.create(name="bar.oregonstate.org")
        for dom in [self.o, self.o_e, self.b_o_e]:
            self.ctnr.domains.add(dom)

    def create_mx(self, **kwargs):
        kwargs.setdefault('ctnr', self.ctnr)
        return MX.objects.create(**kwargs)

    @property
    def objs(self):
        """Create objects for test_create_delete."""
        return (
            self.create_mx(
                label='osumail', domain=self.o, server='relay.oregonstate.edu',
                priority=2, ttl=2222),
            self.create_mx(
                label='', domain=self.o_e, server='mail.sdf.fo', priority=9,
                ttl=34234),
            self.create_mx(
                label='mail', domain=self.b_o_e, server='asdf.asdf',
                priority=123, ttl=213),
            self.create_mx(
                label='', domain=self.b_o_e, server='oregonstate.edu',
                priority=2, ttl=2),
            self.create_mx(
                label=u'dsfasdfasdfasdfasdfasdfasdf', domain=self.o,
                server='nope.mail', priority=12, ttl=124),
        )

    def test_add_invalid(self):
        # TLD condition
        self.assertRaises(
            ValidationError, self.create_mx,
            label='',
            domain=self.o,
            server='mail.oregonstate.edu',
            priority=123,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='adsf.com',
            domain=self.o_e,
            server='mail.oregonstate.edu',
            priority=123,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='foo',
            domain=self.o_e,
            server='mail..com',
            priority=34,
            ttl=1234,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='foo.bar',
            domain=self.o_e,
            server='mail.com',
            priority=3,
            ttl=23424,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='asdf#$@',
            domain=self.o_e,
            server='coo.com',
            priority=123,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='asdf',
            domain=self.o_e,
            server='coo.com',
            priority=-1,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='asdf',
            domain=self.o_e,
            server='coo.com',
            priority=65536,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='asdf',
            domain=self.o_e,
            server=234,
            priority=65536,
            ttl=23,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='a',
            domain=self.o_e,
            server='foo',
            priority=6556,
            ttl=91234241254,
        )

    def do_remove(self, **data):
        mx = self.create_mx(**data)
        mx.delete()
        self.assertFalse(MX.objects.filter(**data).exists())

    def test_remove(self):
        self.do_remove(
            label='',
            domain=self.o_e,
            server='frelay.oregonstate.edu',
            priority=2,
            ttl=2222,
        )

        self.do_remove(
            label='',
            domain=self.o_e,
            server='fmail.sdf.fo',
            priority=9,
            ttl=34234,
        )

        self.do_remove(
            label='mail',
            domain=self.b_o_e,
            server='asdff.asdf',
            priority=123,
            ttl=213,
        )

        self.do_remove(
            label='',
            domain=self.b_o_e,
            server='oregonsftate.edu',
            priority=2,
            ttl=2,
        )

        self.do_remove(
            label=u'dsfasdfasdfasdfasdfasdfasdf',
            domain=self.o,
            server='nopef.mail',
            priority=12,
            ttl=124,
        )

    def test_add_and_update_dup(self):
        mx0 = self.create_mx(
            label='',
            domain=self.o_e,
            server='relaydf.oregonstate.edu',
            priority=2,
            ttl=2222,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='',
            domain=self.o_e,
            server='relaydf.oregonstate.edu',
            priority=2,
            ttl=9800,
        )

        def y():
            self.create_mx(
                label='',
                domain=self.o_e,
                server='mail.sddf.fo',
                priority=9,
                ttl=34234,
            )

        y()

        self.assertRaises(ValidationError, y)

        mx0.server = "mail.sddf.fo"
        mx0.priority = 9
        mx0.ttl = 10000
        self.assertRaises(ValidationError, mx0.save)

    def test_add_with_cname(self):
        cn = CNAME.objects.create(
            label='cnamederp',
            domain=self.o_e,
            target='foo.com',
            ctnr=self.ctnr,
        )

        self.assertRaises(
            ValidationError, self.create_mx,
            label='',
            domain=self.o_e,
            server='cnamederp.oregonstate.org',
            priority=2,
            ttl=2222,
        )

    def test_domain_ctnr(self):
        """Test that an MX's domain must be in the MX's container"""

        ctnr1 = Ctnr(name='test_ctnr1')
        ctnr1.save()
        ctnr1.domains.add(self.o_e)

        MX.objects.create(
            label='foo',
            domain=self.o_e,
            server='bar.oregonstate.edu',
            priority=1,
            ttl=1000,
            ctnr=ctnr1,
        )

        ctnr2 = Ctnr(name='test_ctnr2')
        ctnr2.save()

        self.assertRaises(
            ValidationError, MX.objects.create,
            label='bleh',
            domain=self.o_e,
            server='xyz.oregonstate.edu',
            priority=1,
            ttl=1000,
            ctnr=ctnr2,
        )

    def test_sshfp_txt_name(self):
        """Test that an MX can share a name with an SSHFP or a TXT"""

        def create_mx():
            return MX.objects.create(
                label='foo',
                domain=self.o_e,
                server='bar.oregonstate.edu',
                priority=1,
                ttl=1000,
                ctnr=self.ctnr,
            )
        create_mx.name = 'MX'

        def create_sshfp():
            return SSHFP.objects.create(
                label='foo',
                domain=self.o_e,
                key='7d97e98f8af710c7e7fe703abc8f639e0ee507c4',
                algorithm_number=1,
                fingerprint_type=1,
                ctnr=self.ctnr,
            )
        create_sshfp.name = 'SSHFP'

        def create_txt():
            return TXT.objects.create(
                label='foo',
                domain=self.o_e,
                txt_data='Hi, Mom!',
                ctnr=self.ctnr,
            )
        create_txt.name = 'TXT'

        self.assertObjectsDontConflict((create_mx, create_sshfp, create_txt))
